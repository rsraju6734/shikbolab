-- =====================================================================
-- ShikboLab backend schema (Supabase / PostgreSQL)  —  Phase 9 কিট
-- ⚠️ এটা "তৈরি-করা-নকশা"। Supabase এ রান না করা পর্যন্ত কিছুই সংযুক্ত নয়।
-- রান করার ক্রম: 01_schema.sql  →  02_security.sql  →  03_functions.sql
-- =====================================================================
create extension if not exists pgcrypto;

create type app_role as enum ('super_admin','admin','teacher','editor','student');

-- ব্যবহারকারীর প্রোফাইল (পাসওয়ার্ড এখানে থাকে না; Supabase Auth সামলায়)
create table profiles (
  id          uuid primary key references auth.users(id) on delete cascade,
  full_name   text check (char_length(full_name) <= 80),
  role        app_role not null default 'student',
  class_grade int  check (class_grade between 1 and 12),
  school      text check (char_length(school) <= 120),
  suspended   boolean not null default false,
  created_at  timestamptz not null default now()
);

-- কোন রোলের কী পারমিশন (admin-people.js এর PERMS এর সাথে মিল রাখা)
create table role_permissions (
  role app_role not null,
  perm text not null,
  primary key (role, perm)
);

-- শিক্ষক কোন ক্লাস-রেঞ্জ দেখতে পারবে
create table teacher_classes (
  teacher    uuid not null references profiles(id) on delete cascade,
  grade_from int not null check (grade_from between 1 and 12),
  grade_to   int not null check (grade_to between 1 and 12),
  check (grade_to >= grade_from),
  primary key (teacher, grade_from, grade_to)
);

create table plans (
  key            text primary key check (key ~ '^[a-z0-9_]{1,24}$'),
  name           text not null,
  price_month    numeric(10,2) not null default 0 check (price_month >= 0),
  price_week     numeric(10,2) not null default 0 check (price_week >= 0),
  days_month     int not null default 30 check (days_month between 1 and 400),
  days_week      int not null default 7  check (days_week  between 1 and 400),
  students_limit int not null default 1 check (students_limit >= 1),
  teachers_limit int not null default 0 check (teachers_limit >= 0),
  devices_limit  int not null default 2 check (devices_limit >= 1),
  features       jsonb not null default '[]',
  active         boolean not null default true
);

create table subscriptions (
  id          uuid primary key default gen_random_uuid(),
  owner       uuid not null references profiles(id) on delete cascade,
  plan_key    text references plans(key),
  trial_until timestamptz,
  paid_until  timestamptz,
  created_at  timestamptz not null default now(),
  unique (owner)
);

-- গ্রাহকের পেমেন্ট অনুরোধ (এখনকার ম্যানুয়াল bKash/Nagad + TrxID পদ্ধতি)
create table payment_requests (
  id          uuid primary key default gen_random_uuid(),
  owner       uuid not null references profiles(id) on delete cascade,
  plan_key    text not null references plans(key),
  period      text not null check (period in ('month','week')),
  amount      numeric(10,2) not null check (amount >= 0),
  method      text not null check (method in ('bkash','nagad','other')),
  txn_ref     text not null check (char_length(txn_ref) between 4 and 40),
  status      text not null default 'pending' check (status in ('pending','approved','rejected')),
  created_at  timestamptz not null default now(),
  reviewed_by uuid references profiles(id),
  reviewed_at timestamptz
);
-- একই TrxID দুইবার ব্যবহার ঠেকাতে
create unique index payment_requests_txn_uq on payment_requests (method, lower(txn_ref));

-- নিশ্চিত হওয়া পেমেন্ট। শুধু ফাংশন (বা ভবিষ্যতের গেটওয়ে webhook) এখানে লেখে।
create table payments (
  id                   uuid primary key default gen_random_uuid(),
  owner                uuid not null references profiles(id) on delete cascade,
  request_id           uuid references payment_requests(id),
  plan_key             text not null references plans(key),
  period               text not null check (period in ('month','week')),
  amount               numeric(10,2) not null check (amount >= 0),
  method               text not null,
  txn_ref              text,
  status               text not null default 'confirmed' check (status in ('confirmed','refunded')),
  provider             text not null default 'manual',
  verified_by_provider boolean not null default false,  -- গেটওয়ে server-verify হলে তবেই true
  confirmed_by         uuid references profiles(id),
  confirmed_at         timestamptz not null default now(),
  refunded_at          timestamptz,
  refund_reason        text check (char_length(refund_reason) <= 120)
);

create table progress (
  user_id      uuid not null references profiles(id) on delete cascade,
  slot         text not null check (char_length(slot) <= 20),   -- পরিবারের কোন সদস্য
  chapter_file text not null check (char_length(chapter_file) <= 80),
  score        int not null check (score >= 0),
  total        int not null check (total > 0),
  pct          int not null check (pct between 0 and 100),
  updated_at   timestamptz not null default now(),
  primary key (user_id, slot, chapter_file)
);

-- দর্শক ইভেন্ট (পেজ ভিউ, ল্যাব ব্যবহার ইত্যাদি)। ব্যক্তিগত তথ্য নেই।
create table events (
  id      bigint generated always as identity primary key,
  user_id uuid references profiles(id) on delete set null,
  kind    text not null check (kind in ('page_view','lab_open','quiz_start','quiz_finish','lesson_open')),
  target  text check (char_length(target) <= 100),
  at      timestamptz not null default now()
);
create index events_at_idx on events (at);

create table announcements (
  id        uuid primary key default gen_random_uuid(),
  title     text not null check (char_length(title) <= 80),
  body      text not null check (char_length(body) <= 300),
  level     text not null default 'info' check (level in ('info','warn','good')),
  grade_from int check (grade_from between 1 and 12),
  grade_to   int check (grade_to between 1 and 12),
  starts_at timestamptz,
  ends_at   timestamptz,
  active    boolean not null default true,
  created_by uuid references profiles(id)
);

create table site_settings (
  key        text primary key check (char_length(key) <= 40),
  value      jsonb not null,
  updated_by uuid references profiles(id),
  updated_at timestamptz not null default now()
);

-- বদলানো-যায়-না অডিট লগ
create table audit_log (
  id         bigint generated always as identity primary key,
  at         timestamptz not null default now(),
  actor      uuid,
  actor_role app_role,
  action     text not null,
  entity     text not null,
  entity_id  text,
  detail     jsonb
);
