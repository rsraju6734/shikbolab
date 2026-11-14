/* নতুন chapter যোগ করতে শুধু নিচের list-এ একটা নতুন লাইন যোগ করবে।
   subject: chemistry / physics / math / biology
   status : 'live' (খোলা যাবে) অথবা 'soon' (শীঘ্রই আসছে)
   extra  : true দিলে সেটা নিচের 'বোনাস এক্সট্রা ল্যাব' অংশে যাবে (না দিলে বিষয়ের ভেতরের অধ্যায় হবে)  */
window.CHAPTERS = [
  { subject:'chemistry', title:'রসায়নের ধারণা (অধ্যায় ১)', desc:'রসায়নের ইতিহাস, দৈনন্দিন জীবনে রসায়ন, গবেষণা ও ল্যাবের নিরাপত্তা: নিজে করে শেখো।', file:'chapters/chem-concepts-of-chemistry.html', status:'live' },
  { subject:'chemistry', title:'পর্যায় সারণি (অধ্যায় ৪)', desc:'সব ১১৮টি মৌলের ঠিকানা খুঁজো: ইলেকট্রন ঘুরতে দেখো, পর্যায় ও গ্রুপ বের করো।', file:'chapters/chem-periodic-table.html', status:'live' },
  { subject:'chemistry', title:'রাসায়নিক বিক্রিয়া (অধ্যায় ৭)', desc:'বিক্রিয়ার ধরন চেনো, ইলেকট্রন স্থানান্তর ও জারণ সংখ্যা নিজে করে দেখো।', file:'chapters/chem-chemical-reactions.html', status:'live' },
  { subject:'chemistry', title:'খনিজ সম্পদ: জীবাশ্ম (অধ্যায় ১১)', desc:'পেট্রোলিয়ামের আংশিক পাতন দেখো, হাইড্রোকার্বনের গঠন নিজে বানাও।', file:'chapters/chem-fossil-hydrocarbon.html', status:'live' },
  { subject:'chemistry', title:'⚗️ মৌল মেশানোর ল্যাব (বিশেষ)', desc:'১১৮টা মৌলের যেকোনো ২ থেকে ২০টা মিশিয়ে দেখো: আগুন, রং, বিস্ফোরণ আর ব্যবহার।', file:'chapters/chem-element-mixer.html', status:'live', extra:true },
  { subject:'chemistry', title:'অম্ল-ক্ষার ও নিরপেক্ষকরণ', desc:'অম্ল ও ক্ষার মিশিয়ে pH বদলাতে দেখো, কণার নড়াচড়া দেখো।', file:'chapters/chem-acid-base.html', status:'live' },
  { subject:'physics',   title:'⚡ বৈদ্যুতিক সার্কিট (বিশেষ)', desc:'ওহমের সূত্র পরীক্ষা করো, শ্রেণি ও সমান্তরাল সংযোগে বাল্ব জ্বালাও।', file:'chapters/phy-electric-circuits.html', status:'live', extra:true },
  { subject:'math',      title:'📈 ফাংশন ও গ্রাফ (বিশেষ)', desc:'স্লাইডার নেড়ে সরলরেখা ও দ্বিঘাত ফাংশনের গ্রাফ বদলাতে দেখো, সমীকরণ সমাধান করো।', file:'chapters/math-functions-graphs.html', status:'live', extra:true },
  { subject:'biology',   title:'🧬 বংশগতি: মেন্ডেলের ল্যাব (বিশেষ)', desc:'পানেট বর্গ বানাও, ৩ : ১ ও ৯ : ৩ : ৩ : ১ অনুপাত নিজে বের করো, রক্তের গ্রুপ ও লিঙ্গ নির্ধারণ দেখো।', file:'chapters/bio-heredity-mendel.html', status:'live', extra:true }
];