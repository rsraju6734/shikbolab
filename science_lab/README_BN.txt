ShikboLab SaaS - চালানোর নিয়ম (Windows + VS Code)
===================================================
১) এই ফোল্ডারটা Desktop-এ রাখো (নাম: shikbolab_saas) এবং VS Code-এ খোলো।
২) Terminal খুলে (Ctrl + `) চালাও:
       pip install flask
       python app.py
३) প্রথমবার চালালে terminal-এ তোমার অ্যাডমিন ইউজারনেম ও পাসওয়ার্ড দেখাবে। সেটা লিখে রাখো!
४) ব্রাউজারে খোলো:  http://localhost:5000
   অ্যাডমিন প্যানেল:  http://localhost:5000/admin

কী কী বদলাতে হবে (app.py-এর একদম উপরে):
  - PAY_NUMBERS  : তোমার বিকাশ/নগদ নাম্বার
  - PLANS        : প্ল্যানের দাম ও লিমিট
  - TRIAL_DAYS   : ডেমোর দিন (৭ বা ১৫)
  - FREE_CHAPTERS: লগইন ছাড়া যে অধ্যায় সবাই দেখতে পারবে

নতুন অধ্যায় যোগ করলে:
  তোমার science_lab ফোল্ডারের chapters/ ও js/chapters.js এই প্রজেক্টের content/ ফোল্ডারে কপি করো।

ফাইল কোনটা কী:
  app.py        - পুরো সার্ভার (লগইন, প্ল্যান, লিমিট, অ্যাডমিন, পেমেন্ট)
  templates/    - পেজের ডিজাইন
  static/       - CSS ও অগ্রগতি ট্র্যাকিং স্ক্রিপ্ট
  content/      - তোমার science_lab (হোমপেজ + সব অধ্যায়)
  shikbolab.db  - ডাটাবেস (নিজে তৈরি হবে, মুছো না!)
  uploads/      - স্কুলের লোগো

অনলাইনে ছাড়ার সময় (পরে): hosting + domain + SSL লাগবে। তখন:
  - gunicorn দিয়ে চালাও:  gunicorn app:app
  - HTTPS=1 এবং SECRET_KEY ও ADMIN_PASS environment variable দিও
  - shikbolab.db নিয়মিত ব্যাকআপ রেখো
