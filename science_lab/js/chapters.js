/* নতুন chapter যোগ করতে শুধু নিচের list-এ একটা নতুন লাইন যোগ করবে।
   subject: chemistry / physics / math / biology
   status : 'live' (খোলা যাবে) অথবা 'soon' (শীঘ্রই আসছে)
   extra  : true দিলে সেটা নিচের 'বোনাস এক্সট্রা ল্যাব' অংশে যাবে (না দিলে বিষয়ের ভেতরের অধ্যায় হবে)  */
window.CHAPTERS = [
  { subject:'chemistry', title:'রসায়নের ধারণা (অধ্যায় ১)', desc:'রসায়নের ইতিহাস, দৈনন্দিন জীবনে রসায়ন, গবেষণা ও ল্যাবের নিরাপত্তা: নিজে করে শেখো।', file:'chapters/chem-concepts-of-chemistry.html', status:'live' },
  { subject:'chemistry', title:'পদার্থের অবস্থা (অধ্যায় ২)', desc:'কণার গতি দেখো, ব্যাপন ও নিঃসরণ পরীক্ষা করো, বরফ থেকে বাষ্পের লেখচিত্র নিজে আঁকো।', file:'chapters/chem-states-of-matter.html', status:'live' },
  { subject:'chemistry', title:'পদার্থের গঠন (অধ্যায় ৩)', desc:'প্রোটন-নিউট্রন-ইলেকট্রন দিয়ে পরমাণু গড়ো, রাদারফোর্ড ও বোর মডেল দেখো, ইলেকট্রন বিন্যাস ভরাও, আইসোটোপ ও আপেক্ষিক ভর হিসাব করো।', file:'chapters/chem-structure-of-matter.html', status:'live' },
  { subject:'chemistry', title:'পর্যায় সারণি (অধ্যায় ৪)', desc:'সব ১১৮টি মৌলের ঠিকানা খুঁজো: ইলেকট্রন ঘুরতে দেখো, পর্যায় ও গ্রুপ বের করো।', file:'chapters/chem-periodic-table.html', status:'live' },
  { subject:'chemistry', title:'রাসায়নিক বন্ধন (অধ্যায় ৫)', desc:'যোজ্যতা ইলেকট্রন গুনো, সংকেত বানাও, আয়নিক ও সমযোজী বন্ধন তৈরি হতে দেখো, দ্রাব্যতা ও বিদ্যুৎ পরিবাহিতা পরীক্ষা করো।', file:'chapters/chem-chemical-bond.html', status:'live' },
  { subject:'chemistry', title:'মোলের ধারণা ও রাসায়নিক গণনা (অধ্যায় ৬)', desc:'গ্রাম-মোল-কণা-আয়তন কনভার্টার, ২২.৪ লিটার গ্যাসের বাক্স, মোলার দ্রবণ বানানো, শতকরা সংযুতি, সমীকরণের সমতা ও লিমিটিং বিক্রিয়ক।', file:'chapters/chem-mole-concept.html', status:'live' },
  { subject:'chemistry', title:'রাসায়নিক বিক্রিয়া (অধ্যায় ৭)', desc:'বিক্রিয়ার ধরন চেনো, ইলেকট্রন স্থানান্তর ও জারণ সংখ্যা নিজে করে দেখো।', file:'chapters/chem-chemical-reactions.html', status:'live' },
  { subject:'chemistry', title:'রসায়ন ও শক্তি (অধ্যায় ৮)', desc:'ΔH ও বন্ধন শক্তির হিসাব, জ্বালানির ক্ষতি, তড়িৎ বিশ্লেষণ, ইলেকট্রোপ্লেটিং, গ্যালভানিক কোষ ও নিউক্লিয়ার চেইন বিক্রিয়া।', file:'chapters/chem-chemistry-energy.html', status:'live' },
  { subject:'chemistry', title:'এসিড-ক্ষারক সমতা (অধ্যায় ৯)', desc:'pH স্কেলে রং বদলাও, এসিডের বিক্রিয়া ও চুনের পানি দেখো, সবল-দুর্বল এসিডে বাল্ব জ্বালাও, প্রশমন, এসিড বৃষ্টি, পানির খরতা ও বিশুদ্ধকরণ।', file:'chapters/chem-acid-base-balance.html', status:'live' },
  { subject:'chemistry', title:'খনিজ সম্পদ: ধাতু-অধাতু (অধ্যায় ১০)', desc:'আকরিকের ঘনীকরণ, ভস্মীকরণ-তাপজারণ, সক্রিয়তা সিরিজ, Al ও Cu-এর তড়িৎ বিশ্লেষণ, বাত্যা চুল্লি, সংকর ধাতু, মরিচা এবং সালফার ও H₂SO₄ তৈরি দেখো।', file:'chapters/chem-metals-nonmetals.html', status:'live' },
  { subject:'chemistry', title:'খনিজ সম্পদ: জীবাশ্ম (অধ্যায় ১১)', desc:'পেট্রোলিয়ামের আংশিক পাতন দেখো, হাইড্রোকার্বনের গঠন নিজে বানাও।', file:'chapters/chem-fossil-hydrocarbon.html', status:'live' },
  { subject:'chemistry', title:'আমাদের জীবনে রসায়ন (অধ্যায় ১২)', desc:'লবণ চাষ, বেকিং পাউডার, ভিনেগার, সাবান ও ডিটারজেন্ট, ব্লিচিং পাউডার, অ্যামোনিয়ার হেবার পদ্ধতি, ইউরিয়া সার, আম পাকানো ও প্রিজারভেটিভ নিজে চালিয়ে দেখো।', file:'chapters/chem-life-chemistry.html', status:'live' },
  { subject:'chemistry', title:'⚗️ মৌল মেশানোর ল্যাব (বিশেষ)', desc:'১১৮টা মৌলের যেকোনো ২ থেকে ২০টা মিশিয়ে দেখো: আগুন, রং, বিস্ফোরণ আর ব্যবহার।', file:'chapters/chem-element-mixer.html', status:'live', extra:true },
  { subject:'chemistry', title:'অম্ল-ক্ষার ও নিরপেক্ষকরণ', desc:'অম্ল ও ক্ষার মিশিয়ে pH বদলাতে দেখো, কণার নড়াচড়া দেখো।', file:'chapters/chem-acid-base.html', status:'live' },
  { subject:'chemistry', title:'⚗️ টাইট্রেশন ল্যাব (বিশেষ)', desc:'বুরেট থেকে ফোঁটা ফোঁটা NaOH দিয়ে অজানা এসিডের ঘনমাত্রা বের করো, সাথে pH বক্ররেখা দেখো।', file:'chapters/chem-x-titration.html', status:'live', extra:true },
  { subject:'chemistry', title:'🌈 pH ও নির্দেশক ল্যাব (বিশেষ)', desc:'লেবুর রস থেকে সাবান-পানি পর্যন্ত ১৩টি জিনিসে ৪ রকম নির্দেশক ও pH মিটার ব্যবহার করে দেখো।', file:'chapters/chem-x-ph-indicator.html', status:'live', extra:true },
  { subject:'chemistry', title:'🔥 শিখা পরীক্ষা ল্যাব (বিশেষ)', desc:'৭টি ধাতব লবণ শিখায় ধরে রং ও বর্ণালি রেখা দেখো, তারপর অজানা লবণ চিনে নাও।', file:'chapters/chem-x-flame-test.html', status:'live', extra:true },
  { subject:'chemistry', title:'🧪 দ্রবণ তৈরি ও লঘুকরণ ল্যাব (বিশেষ)', desc:'নির্দিষ্ট মোলারিটির দ্রবণ ধাপে ধাপে বানাও এবং M₁V₁ = M₂V₂ দিয়ে লঘু করো।', file:'chapters/chem-x-solution-dilution.html', status:'live', extra:true },
  { subject:'chemistry', title:'🥽 ল্যাব নিরাপত্তা ও যন্ত্রপাতি (বিশেষ)', desc:'১০টি যন্ত্র চেনো, মেনিসকাস পড়া শেখো এবং ল্যাবে নিরাপদ থাকার নিয়ম খেলায় খেলায় শেখো।', file:'chapters/chem-x-lab-safety.html', status:'live', extra:true },
  { subject:'physics',   title:'ভৌত রাশি এবং তাদের পরিমাপ (অধ্যায় ১)', desc:'পদার্থবিজ্ঞানের সময়রেখা, SI-এর সাত একক, উপসর্গ ও মাত্রা, স্লাইড ক্যালিপার্স, স্ক্রু-গেজ আর পরিমাপের ত্রুটি নিজে হাতে করে দেখো।', file:'chapters/phy-physical-quantities.html', status:'live' },
  { subject:'physics',   title:'গতি (অধ্যায় ২)', desc:'আপেক্ষিক গতি, দূরত্ব-সরণ, দ্রুতি-বেগ, ত্বরণ, গতির সমীকরণ, পড়ন্ত বস্তু ও লেখচিত্র — ১০টি অ্যানিমেটেড ল্যাব', file:'chapters/phy-motion.html', status:'live' },
  { subject:'physics', title:'বল (অধ্যায় ৩)', desc:'জড়তা, চার মৌলিক বল, ভরবেগ ও সংঘর্ষ, F = ma, মহাকর্ষ, ক্রিয়া-প্রতিক্রিয়া ও ঘর্ষণ — অ্যানিমেটেড ল্যাব', file:'chapters/phy-force.html', status:'live' },
  { subject:'physics', title:'কাজ, ক্ষমতা ও শক্তি (অধ্যায় ৪)', desc:'কাজ W = Fs, গতিশক্তি ও বিভব শক্তি, শক্তির নিত্যতা ও রূপান্তর, শক্তির উৎস, E = mc², ক্ষমতা ও কর্মদক্ষতা — ১১টি অ্যানিমেটেড ল্যাব', file:'chapters/phy-energy.html', status:'live' },
  { subject:'physics',   title:'⚡ বৈদ্যুতিক সার্কিট (বিশেষ)', desc:'ওহমের সূত্র পরীক্ষা করো, শ্রেণি ও সমান্তরাল সংযোগে বাল্ব জ্বালাও।', file:'chapters/phy-electric-circuits.html', status:'live', extra:true },
  { subject:'math',      title:'📈 ফাংশন ও গ্রাফ (বিশেষ)', desc:'স্লাইডার নেড়ে সরলরেখা ও দ্বিঘাত ফাংশনের গ্রাফ বদলাতে দেখো, সমীকরণ সমাধান করো।', file:'chapters/math-functions-graphs.html', status:'live', extra:true },
  { subject:'biology',   title:'🧬 বংশগতি: মেন্ডেলের ল্যাব (বিশেষ)', desc:'পানেট বর্গ বানাও, ৩ : ১ ও ৯ : ৩ : ৩ : ১ অনুপাত নিজে বের করো, রক্তের গ্রুপ ও লিঙ্গ নির্ধারণ দেখো।', file:'chapters/bio-heredity-mendel.html', status:'live', extra:true }
];
