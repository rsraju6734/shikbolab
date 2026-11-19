-- =====================================================================
-- ShikboLab: নতুন ইউজার ট্রিগার + স্টাফের নিরাপদ অ্যাকশন ফাংশন
-- আগে 01 ও 02 রান করো।
-- =====================================================================

-- নতুন ইউজার সাইন-আপ করলে প্রোফাইল ও ট্রায়াল সাবস্ক্রিপশন বানায়।
-- role সবসময় 'student'। সাইন-আপ ফর্ম থেকে role দেওয়ার কোনো রাস্তা নেই।
create or replace function public.handle_new_user() returns trigger
language plpgsql security definer set search_path = public as $$
declare td int := 7;
begin
  begin td := least(90, greatest(1, (select (value)::int from site_settings where key = 'trial_days')));
  exception when others then td := 7; end;
  if td is null then td := 7; end if;
  insert into profiles (id, full_name, role)
  values (new.id, left(coalesce(new.raw_user_meta_data->>'full_name',''), 80), 'student');
  insert into subscriptions (owner, trial_until) values (new.id, now() + make_interval(days => td));
  return new;
end $$;
create trigger on_auth_user_created after insert on auth.users
  for each row execute function public.handle_new_user();

-- পেমেন্ট অনুরোধ নিশ্চিত করা (ম্যানুয়াল)। মেয়াদ বাড়ে, payments এ সারি যায়।
create or replace function public.admin_confirm_payment(req uuid) returns void
language plpgsql security definer set search_path = public as $$
declare r payment_requests; p plans; d int;
begin
  if not has_perm('payments.manage') then raise exception 'অনুমতি নেই'; end if;
  select * into r from payment_requests where id = req for update;
  if not found or r.status <> 'pending' then raise exception 'অনুরোধ পাওয়া যায়নি বা আগেই নিষ্পত্তি হয়েছে'; end if;
  select * into p from plans where key = r.plan_key;
  d := case r.period when 'week' then p.days_week else p.days_month end;
  update payment_requests set status = 'approved', reviewed_by = auth.uid(), reviewed_at = now() where id = req;
  insert into payments (owner, request_id, plan_key, period, amount, method, txn_ref, provider, verified_by_provider, confirmed_by)
  values (r.owner, r.id, r.plan_key, r.period, r.amount, r.method, r.txn_ref, 'manual', false, auth.uid());
  update subscriptions set plan_key = r.plan_key,
         paid_until = greatest(coalesce(paid_until, now()), now()) + make_interval(days => d)
   where owner = r.owner;
end $$;

create or replace function public.admin_reject_payment(req uuid) returns void
language plpgsql security definer set search_path = public as $$
begin
  if not has_perm('payments.manage') then raise exception 'অনুমতি নেই'; end if;
  update payment_requests set status = 'rejected', reviewed_by = auth.uid(), reviewed_at = now()
   where id = req and status = 'pending';
  if not found then raise exception 'অনুরোধ পাওয়া যায়নি বা আগেই নিষ্পত্তি হয়েছে'; end if;
end $$;

create or replace function public.admin_refund_payment(pid uuid, why text, cancel_validity boolean)
returns void language plpgsql security definer set search_path = public as $$
declare r payments;
begin
  if not has_perm('payments.manage') then raise exception 'অনুমতি নেই'; end if;
  select * into r from payments where id = pid for update;
  if not found or r.status <> 'confirmed' then raise exception 'পেমেন্ট পাওয়া যায়নি বা আগেই রিফান্ড হয়েছে'; end if;
  update payments set status = 'refunded', refunded_at = now(), refund_reason = left(coalesce(why,''), 120) where id = pid;
  if cancel_validity then update subscriptions set paid_until = least(coalesce(paid_until, now()), now()) where owner = r.owner; end if;
end $$;

create or replace function public.admin_set_suspended(target uuid, flag boolean) returns void
language plpgsql security definer set search_path = public as $$
begin
  if not has_perm('students.manage') then raise exception 'অনুমতি নেই'; end if;
  if exists (select 1 from profiles where id = target and role = 'super_admin') and not exists (select 1 from profiles where id = auth.uid() and role = 'super_admin')
    then raise exception 'সুপার অ্যাডমিনকে বন্ধ করা যায় না'; end if;
  update profiles set suspended = flag where id = target;
end $$;

-- রোল বদলানো শুধু super_admin পারে; নিজের রোল নিজে বদলানো যায় না।
create or replace function public.admin_set_role(target uuid, new_role app_role) returns void
language plpgsql security definer set search_path = public as $$
begin
  if current_role_name() is distinct from 'super_admin' then raise exception 'শুধু সুপার অ্যাডমিন রোল দিতে পারে'; end if;
  if target = auth.uid() then raise exception 'নিজের রোল নিজে বদলানো যায় না'; end if;
  update profiles set role = new_role where id = target;
end $$;

-- ফাংশন চালানোর অধিকার: শুধু লগইন করা ইউজার (ভেতরে পারমিশন আবার যাচাই হয়)
revoke all on function admin_confirm_payment(uuid), admin_reject_payment(uuid), admin_refund_payment(uuid,text,boolean), admin_set_suspended(uuid,boolean), admin_set_role(uuid,app_role) from public, anon;
grant execute on function admin_confirm_payment(uuid), admin_reject_payment(uuid), admin_refund_payment(uuid,text,boolean), admin_set_suspended(uuid,boolean), admin_set_role(uuid,app_role) to authenticated;
revoke all on function has_perm(text), current_role_name(), teacher_sees(uuid), sees_student(uuid) from public, anon;
grant execute on function has_perm(text), current_role_name(), teacher_sees(uuid), sees_student(uuid) to authenticated;
-- anon এর জন্যও দরকার: পাবলিক policy (plans, announcements) এ has_perm() ডাকা হয়, লগইন ছাড়া সেটা false দেয়।
grant execute on function has_perm(text) to anon;
