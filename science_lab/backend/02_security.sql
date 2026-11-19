-- =====================================================================
-- ShikboLab: পারমিশন-ফাংশন, Row Level Security, অডিট ট্রিগার
-- আগে 01_schema.sql রান করো।
-- মূল নিয়ম: ব্রাউজারে শুধু anon/public key যায়। service_role key কোথাও রাখবে না।
-- =====================================================================

-- ডিফল্ট পারমিশন (admin-people.js এর DEF এর মতো)
insert into role_permissions (role, perm) values
 ('admin','content.view'),('admin','content.edit'),('admin','content.publish'),('admin','labs.manage'),('admin','questions.manage'),('admin','quizzes.manage'),('admin','students.view'),('admin','students.manage'),('admin','teachers.manage'),('admin','payments.view'),('admin','notifications.send'),('admin','analytics.view'),
 ('teacher','content.view'),('teacher','content.edit'),('teacher','questions.manage'),('teacher','quizzes.manage'),('teacher','students.view'),('teacher','analytics.view'),
 ('editor','content.view'),('editor','content.edit'),('editor','labs.manage'),('editor','questions.manage'),('editor','quizzes.manage');
-- super_admin এর জন্য সারি লাগে না: has_perm() এ সব পারমিশন ধরা হয়।

-- বর্তমান ব্যবহারকারীর রোল
create or replace function public.current_role_name() returns app_role
language sql stable security definer set search_path = public as $$
  select role from profiles where id = auth.uid() and not suspended
$$;

create or replace function public.has_perm(p text) returns boolean
language sql stable security definer set search_path = public as $$
  select coalesce((
    select case when pr.role = 'super_admin' then true
                else exists (select 1 from role_permissions rp where rp.role = pr.role and rp.perm = p) end
    from profiles pr where pr.id = auth.uid() and not pr.suspended
  ), false)
$$;

-- শিক্ষক কি এই শিক্ষার্থীকে দেখতে পারে?
create or replace function public.teacher_sees(student uuid) returns boolean
language sql stable security definer set search_path = public as $$
  select exists (
    select 1 from teacher_classes tc join profiles s on s.id = student
    where tc.teacher = auth.uid() and s.class_grade between tc.grade_from and tc.grade_to
      and exists (select 1 from profiles t where t.id = auth.uid() and t.role = 'teacher' and not t.suspended))
$$;

-- কে কার প্রোফাইল/অগ্রগতি দেখতে পারে: নিজে, অ্যাডমিন (সব), শিক্ষক (শুধু নিজের ক্লাস-রেঞ্জ)।
-- শিক্ষকের 'students.view' পারমিশন থাকলেও সে সব ক্লাস দেখবে না। ক্লাস-সীমা teacher_sees() দিয়ে।
create or replace function public.sees_student(student uuid) returns boolean
language sql stable security definer set search_path = public as $$
  select student = auth.uid()
      or (has_perm('students.view') and current_role_name() is distinct from 'teacher')
      or teacher_sees(student)
$$;

-- ---------- সব টেবিলে RLS চালু ----------
alter table profiles          enable row level security;
alter table role_permissions  enable row level security;
alter table teacher_classes   enable row level security;
alter table plans             enable row level security;
alter table subscriptions     enable row level security;
alter table payment_requests  enable row level security;
alter table payments          enable row level security;
alter table progress          enable row level security;
alter table events            enable row level security;
alter table announcements     enable row level security;
alter table site_settings     enable row level security;
alter table audit_log         enable row level security;

-- ---------- টেবিল-লেভেল অধিকার: আগে সব কেড়ে নিয়ে শুধু যা লাগে দেওয়া ----------
revoke all on all tables in schema public from anon, authenticated;
grant select on plans, announcements, site_settings to anon, authenticated;
grant insert on events to anon, authenticated;
grant select on profiles, subscriptions, payment_requests, payments, progress, events, role_permissions, teacher_classes, audit_log to authenticated;
grant insert on payment_requests to authenticated;
grant insert, update on progress to authenticated;
-- প্রোফাইলে নিজে শুধু এই কলামগুলো বদলাতে পারবে (role/suspended নয়):
grant update (full_name, class_grade, school) on profiles to authenticated;
-- স্টাফ কনটেন্ট-টেবিল বদলায় RLS policy দিয়ে:
grant insert, update, delete on plans, announcements, site_settings to authenticated;
grant insert, update, delete on teacher_classes to authenticated;

-- ---------- policies ----------
create policy profiles_read on profiles for select to authenticated
  using (sees_student(id));
create policy profiles_update_own on profiles for update to authenticated
  using (id = auth.uid() and not suspended) with check (id = auth.uid());

create policy perms_read on role_permissions for select to authenticated using (has_perm('staff.manage'));
create policy tc_read  on teacher_classes for select to authenticated using (teacher = auth.uid() or has_perm('teachers.manage'));
create policy tc_write on teacher_classes for all    to authenticated using (has_perm('teachers.manage')) with check (has_perm('teachers.manage'));

create policy plans_public on plans for select to anon, authenticated using (active or has_perm('plans.manage'));
create policy plans_write  on plans for all    to authenticated using (has_perm('plans.manage')) with check (has_perm('plans.manage'));

create policy subs_read on subscriptions for select to authenticated
  using (sees_student(owner) or has_perm('payments.view'));

create policy preq_read on payment_requests for select to authenticated
  using (owner = auth.uid() or has_perm('payments.view'));
-- গ্রাহক শুধু নিজের নামে, শুধু 'pending' অবস্থায় অনুরোধ দিতে পারে
create policy preq_insert on payment_requests for insert to authenticated
  with check (owner = auth.uid() and status = 'pending' and reviewed_by is null and reviewed_at is null
              and exists (select 1 from profiles where id = auth.uid() and not suspended));

create policy pay_read on payments for select to authenticated
  using (owner = auth.uid() or has_perm('payments.view'));
-- payments এ INSERT/UPDATE policy ইচ্ছে করেই নেই: শুধু 03_functions.sql এর ফাংশন লেখে।

create policy prog_read   on progress for select to authenticated
  using (sees_student(user_id));
create policy prog_insert on progress for insert to authenticated with check (user_id = auth.uid());
create policy prog_update on progress for update to authenticated using (user_id = auth.uid()) with check (user_id = auth.uid());

-- ইভেন্ট: যে কেউ জমা দিতে পারে (kind/target ঠিক থাকলে), শুধু স্টাফ পড়তে পারে
-- ⚠️ RLS এ rate-limit হয় না; স্প্যাম ঠেকাতে Supabase Edge Function/Cloudflare নিয়ম লাগবে।
create policy ev_insert on events for insert to anon, authenticated
  with check (user_id is null or user_id = auth.uid());
create policy ev_read on events for select to authenticated using (has_perm('analytics.view'));

create policy ann_public on announcements for select to anon, authenticated
  using ((active and (starts_at is null or starts_at <= now()) and (ends_at is null or ends_at >= now())) or has_perm('notifications.send'));
create policy ann_write on announcements for all to authenticated
  using (has_perm('notifications.send')) with check (has_perm('notifications.send'));

create policy site_public on site_settings for select to anon, authenticated using (true);
create policy site_write  on site_settings for all to authenticated
  using (has_perm('settings.manage')) with check (has_perm('settings.manage'));

create policy audit_read on audit_log for select to authenticated using (has_perm('audit.view'));
-- audit_log এ INSERT/UPDATE/DELETE policy নেই। শুধু নিচের ট্রিগার (security definer) লেখে।

-- অডিট লগ বদলানো/মোছা ঠেকাতে (টেবিল-মালিকও ভুল করে বদলাতে পারবে না)
create or replace function public.audit_immutable() returns trigger language plpgsql as $$
begin raise exception 'audit_log বদলানো বা মোছা যায় না'; end $$;
create trigger audit_no_update before update or delete on audit_log
  for each row execute function audit_immutable();

-- ---------- অডিট ট্রিগার ----------
create or replace function public.log_audit() returns trigger
language plpgsql security definer set search_path = public as $$
declare rid text; j jsonb;
begin
  j := case when tg_op = 'DELETE' then to_jsonb(old) else to_jsonb(new) end;
  rid := coalesce(j->>'id', j->>'key');
  -- গোপন/বড় ফিল্ড বাদ
  j := j - 'features';
  insert into audit_log (actor, actor_role, action, entity, entity_id, detail)
  values (auth.uid(), current_role_name(), tg_op, tg_table_name, rid, j);
  return coalesce(new, old);
end $$;

create trigger audit_plans    after insert or update or delete on plans            for each row execute function log_audit();
create trigger audit_pay      after insert or update or delete on payments         for each row execute function log_audit();
create trigger audit_preq     after insert or update           on payment_requests for each row execute function log_audit();
create trigger audit_subs     after insert or update or delete on subscriptions    for each row execute function log_audit();
create trigger audit_site     after insert or update or delete on site_settings    for each row execute function log_audit();
create trigger audit_ann      after insert or update or delete on announcements    for each row execute function log_audit();
create trigger audit_profiles after update of role, suspended   on profiles        for each row execute function log_audit();
