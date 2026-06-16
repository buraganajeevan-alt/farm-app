// Kisan Mitra Super App - Core Logic (2026 Edition)

// --- MOCK DATABASE AND SYSTEM INITIAL STATE ---
const CROP_CATALOG = [
    { id: 'seeds-paddy', category: 'seeds', name: 'Premium Hybrid Paddy Seeds (BPT 5204)', desc: 'High yield, pest-resistant seeds suitable for Kharif season in AP.', price: 1250, unit: 'Bag (25kg)', img: '🌾', stock: 120 },
    { id: 'seeds-cotton', category: 'seeds', name: 'BG-II Bt Cotton Seeds', desc: 'Genetically modified cotton seeds resistant to bollworms. High germination rate.', price: 860, unit: 'Packet (450g)', img: '🌱', stock: 200 },
    { id: 'fertilizer-npk', category: 'fertilizers', name: 'NPK 19-19-19 Fertilizer', desc: 'Water-soluble fertilizer for balanced crop nutrition and early growth stage.', price: 950, unit: 'Bag (50kg)', img: '🧪', stock: 85 },
    { id: 'fertilizer-urea', category: 'fertilizers', name: 'Neem Coated Urea', desc: 'Slow-release urea promoting uniform green canopy growth.', price: 290, unit: 'Bag (45kg)', img: '❄️', stock: 500 },
    { id: 'insect-neem', category: 'chemicals', name: 'Neem-Azal T/S 1% (Organic)', desc: 'Organic neem-based concentrated bio-pesticide for chewing/sucking pests.', price: 450, unit: 'Bottle (500ml)', img: '🧴', stock: 150 },
    { id: 'tool-sprayer', category: 'tools', name: 'Battery Powered Knapsack Sprayer', desc: '16L capacity heavy-duty sprayer with rechargeable 12V battery and dual nozzles.', price: 2800, unit: 'Piece', img: '🎒', stock: 40 },
    { id: 'tool-weeder', category: 'tools', name: 'Mini Power Tiller / Weeder', desc: '3HP petrol engine weeder for inter-culture operations in orchards and field rows.', price: 18500, unit: 'Piece', img: '🚜', stock: 15 }
];

const DEFAULT_TRADE_LISTINGS = [
    { id: 'lst-1', farmer: 'Subba Rao', crop: 'Super Fine Paddy (BPT 5204)', quantity: 80, price: 2150, district: 'Guntur', phone: '9848523120', img: '🌾', date: '2026-06-15' },
    { id: 'lst-2', farmer: 'Ramesh Reddy', crop: 'High-Grade Cotton', quantity: 45, price: 7200, district: 'Krishna', phone: '9177123456', img: '☁️', date: '2026-06-14' },
    { id: 'lst-3', farmer: 'K. Srinivasa Rao', crop: 'Organic Turmeric (Pragati)', quantity: 30, price: 12500, district: 'East Godavari', phone: '9440123987', img: '🍂', date: '2026-06-16' }
];

const MOCK_LABOR_TEAMS = [
    { id: 'team-1', leader: 'Mallesh Yadav', specialization: 'Harvesting', size: 14, rate: 550, location: 'Guntur', contact: '9000123450', rating: 4.8, img: '🚜' },
    { id: 'team-2', leader: 'Sattayya Crew', specialization: 'Sowing', size: 20, rate: 480, location: 'Krishna', contact: '9550123411', rating: 4.7, img: '🌱' },
    { id: 'team-3', leader: 'Bhaskar Plowing Team', specialization: 'Tilling', size: 5, rate: 950, location: 'Visakhapatnam', contact: '9866123422', rating: 4.9, img: '🚜' },
    { id: 'team-4', leader: 'Lakshmi Weeding Group', specialization: 'Weeding', size: 12, rate: 400, location: 'East Godavari', contact: '9912123433', rating: 4.5, img: '🌾' },
    { id: 'team-5', leader: 'Ramulu Spraying Crew', specialization: 'Weeding', size: 8, rate: 600, location: 'Warangal', contact: '9010123444', rating: 4.6, img: '🧴' }
];

const MOCK_MANDI_DATABASE = {
    'Paddy': [
        { mandi: 'Guntur Market Yard', district: 'Guntur', maxPrice: 2280, minPrice: 2050, trend: 1.5 },
        { mandi: 'Anakapalli Mandi', district: 'Visakhapatnam', maxPrice: 2150, minPrice: 1980, trend: -0.8 },
        { mandi: 'Vijayawada Market', district: 'Krishna', maxPrice: 2240, minPrice: 2010, trend: 2.1 },
        { mandi: 'Kakinada Market Yard', district: 'East Godavari', maxPrice: 2220, minPrice: 1990, trend: 0.5 },
        { mandi: 'Warangal Yard', district: 'Warangal', maxPrice: 2300, minPrice: 2080, trend: 1.8 }
    ],
    'Cotton': [
        { mandi: 'Guntur Market Yard', district: 'Guntur', maxPrice: 7450, minPrice: 6900, trend: 3.2 },
        { mandi: 'Vijayawada Market', district: 'Krishna', maxPrice: 7200, minPrice: 6750, trend: 1.1 },
        { mandi: 'Warangal Yard', district: 'Warangal', maxPrice: 7550, minPrice: 7000, trend: -1.2 },
        { mandi: 'Anakapalli Mandi', district: 'Visakhapatnam', maxPrice: 7100, minPrice: 6500, trend: 0.0 }
    ],
    'Turmeric': [
        { mandi: 'Guntur Market Yard', district: 'Guntur', maxPrice: 13500, minPrice: 11200, trend: 4.8 },
        { mandi: 'Kakinada Market Yard', district: 'East Godavari', maxPrice: 12900, minPrice: 10500, trend: 2.5 },
        { mandi: 'Warangal Yard', district: 'Warangal', maxPrice: 13200, minPrice: 11000, trend: -0.5 }
    ],
    'Chilli': [
        { mandi: 'Guntur Market Yard (Asia\'s Largest)', district: 'Guntur', maxPrice: 18500, minPrice: 15000, trend: -2.3 },
        { mandi: 'Vijayawada Market', district: 'Krishna', maxPrice: 17200, minPrice: 14200, trend: 0.8 },
        { mandi: 'Warangal Yard', district: 'Warangal', maxPrice: 19200, minPrice: 15500, trend: 3.5 }
    ],
    'Maize': [
        { mandi: 'Guntur Market Yard', district: 'Guntur', maxPrice: 2150, minPrice: 1880, trend: 0.9 },
        { mandi: 'Vijayawada Market', district: 'Krishna', maxPrice: 2080, minPrice: 1850, trend: -1.1 },
        { mandi: 'Warangal Yard', district: 'Warangal', maxPrice: 2210, minPrice: 1920, trend: 1.4 },
        { mandi: 'Anakapalli Mandi', district: 'Visakhapatnam', maxPrice: 2020, minPrice: 1800, trend: 0.2 }
    ]
};

// Weekly historical data for trend chart (simulating price logs in ₹/Quintal)
const WEEKLY_TRENDS = {
    'Paddy': [2100, 2120, 2150, 2140, 2170, 2190, 2220],
    'Cotton': [7050, 7120, 7180, 7250, 7300, 7290, 7325],
    'Turmeric': [11800, 11950, 12200, 12400, 12600, 12850, 13200],
    'Chilli': [18200, 18400, 18100, 17900, 17500, 17800, 17400],
    'Maize': [1980, 2010, 2030, 2000, 2020, 2045, 2080]
};

// Database of regional agricultural hubs in Andhra Pradesh and Telangana with GPS Coordinates
const LOCATION_DATABASE = {
    'Anakapalli': { state: 'Andhra Pradesh', lat: 17.6895, lon: 83.0028, temp: '31°C', condition: 'Partly Cloudy • Humidity 74%', icon: '⛅', alert: 'Normal Weather', advisoryTitle: 'Sugarcane Irrigation', advisoryBody: 'Moderate humidity. Irrigate sugarcane plots regularly to prevent early shoot borer.', advisoryIcon: 'ℹ️' },
    'Ananthapuramu': { state: 'Andhra Pradesh', lat: 14.6819, lon: 77.6006, temp: '38°C', condition: 'Hot & Dry • Humidity 35%', icon: '☀️', alert: 'Drought Warning', advisoryTitle: 'Micro-Irrigation Sowing', advisoryBody: 'Severe dry weather. Drip irrigation is highly recommended for Groundnuts to save water.', advisoryIcon: '🔥' },
    'Annamayya': { state: 'Andhra Pradesh', lat: 14.0500, lon: 78.7500, temp: '34°C', condition: 'Sunny • Humidity 45%', icon: '☀️', alert: 'Normal Weather', advisoryTitle: 'Horticulture Crops', advisoryBody: 'Warm dry weather. Rayachoti region farmers are advised to cover sweet orange and papaya orchards with mulch to reduce soil moisture evaporation.', advisoryIcon: 'ℹ️' },
    'Alluri Sitharama Raju': { state: 'Andhra Pradesh', lat: 18.0805, lon: 82.6625, temp: '26°C', condition: 'Cool & Rainy • Humidity 90%', icon: '🌧️', alert: 'Landslide Warning', advisoryTitle: 'Hill Slope Farming', advisoryBody: 'Heavy rains in ghats. Ensure proper contour drainage in coffee and pepper plantations to avoid soil erosion.', advisoryIcon: '⚠️' },
    'Bapatla': { state: 'Andhra Pradesh', lat: 15.9044, lon: 80.4682, temp: '32°C', condition: 'Windy • Humidity 80%', icon: '💨', alert: 'High Winds Alert', advisoryTitle: 'Paddy Nursery Windbreaks', advisoryBody: 'Strong coastal winds. Shelter paddy nurseries using windbreaks. Spray zinc sulfate if leaves show yellowing.', advisoryIcon: '⚠️' },
    'Chittoor': { state: 'Andhra Pradesh', lat: 13.2172, lon: 79.1003, temp: '33°C', condition: 'Partly Cloudy • Humidity 60%', icon: '⛅', alert: 'Normal Weather', advisoryTitle: 'Tomato Crop Advice', advisoryBody: 'Warm days. Staking tomato crops is advised to prevent leaf spot fungal infections from soil contact.', advisoryIcon: 'ℹ️' },
    'East Godavari': { state: 'Andhra Pradesh', lat: 17.0005, lon: 81.8040, temp: '32°C', condition: 'Rain • Humidity 85%', icon: '🌧️', alert: 'Pre-Monsoon Alert', advisoryTitle: 'Nursery Prep', advisoryBody: 'Monsoon approaching. Keep fields ready for transplantation. Spray copper oxychloride for leaf spot.', advisoryIcon: '⚠️' },
    'Eluru': { state: 'Andhra Pradesh', lat: 16.7107, lon: 81.1018, temp: '33°C', condition: 'Humid • Humidity 82%', icon: '☁️', alert: 'Normal Weather', advisoryTitle: 'Paddy Weeding', advisoryBody: 'High humidity favors weeds. Conduct manual weeding 15 days after paddy sowing. Keep water level at 2cm.', advisoryIcon: 'ℹ️' },
    'Guntur': { state: 'Andhra Pradesh', lat: 16.3067, lon: 80.4365, temp: '35°C', condition: 'Sunny • Humidity 51%', icon: '☀️', alert: 'Dry Soil Warning', advisoryTitle: 'Irrigation & Plowing', advisoryBody: 'Deep summer plowing is advised to expose pests. Check soil moisture before sowing cotton seeds.', advisoryIcon: 'ℹ️' },
    'Kakinada': { state: 'Andhra Pradesh', lat: 16.9890, lon: 82.2474, temp: '29°C', condition: 'Thunderstorm • Humidity 88%', icon: '⛈️', alert: 'Storm Advisory', advisoryTitle: 'Drainage Systems', advisoryBody: 'Heavy thunderstorms forecast. Clear agricultural drainage ditches. Postpone fertilizer broadcasting.', advisoryIcon: '⚠️' },
    'Konaseema': { state: 'Andhra Pradesh', lat: 16.5787, lon: 82.0061, temp: '30°C', condition: 'Rain • Humidity 86%', icon: '🌧️', alert: 'Monsoon Alert', advisoryTitle: 'Coconut Leaf Management', advisoryBody: 'Clean crown areas in coconut palms to prevent rhinoceros beetle infestation. Keep drainage open.', advisoryIcon: '⚠️' },
    'Krishna': { state: 'Andhra Pradesh', lat: 16.1809, lon: 81.1303, temp: '32°C', condition: 'Light Rain • Humidity 78%', icon: '🌦️', alert: 'Humid Weather Alert', advisoryTitle: 'Fungal Infection Risk', advisoryBody: 'High relative humidity. Monitor paddy nurseries for blast. Keep field channels clean for drainage.', advisoryIcon: '⚠️' },
    'Kurnool': { state: 'Andhra Pradesh', lat: 15.8281, lon: 78.0373, temp: '37°C', condition: 'Sunny • Humidity 44%', icon: '☀️', alert: 'Dry Soil Warning', advisoryTitle: 'Crop Hydration', advisoryBody: 'High temperature conditions. Provide early morning irrigation to protect crop nurseries.', advisoryIcon: 'ℹ️' },
    'Nandyal': { state: 'Andhra Pradesh', lat: 15.4831, lon: 78.4870, temp: '36°C', condition: 'Clear Sky • Humidity 40%', icon: '☀️', alert: 'High Heat Warning', advisoryTitle: 'Cotton Sowing Prep', advisoryBody: 'Hot conditions continue. Prepare lands for cotton. Apply farmyard manure to retain soil moisture.', advisoryIcon: 'ℹ️' },
    'NTR': { state: 'Andhra Pradesh', lat: 16.5062, lon: 80.6480, temp: '33°C', condition: 'Sunny • Humidity 55%', icon: '☀️', alert: 'Normal Weather', advisoryTitle: 'Seed Treatment', advisoryBody: 'Treat paddy seeds with Carbendazim (2g/kg seed) to prevent seed-borne diseases before sowing.', advisoryIcon: 'ℹ️' },
    'Palnadu': { state: 'Andhra Pradesh', lat: 16.2361, lon: 80.0510, temp: '36°C', condition: 'Sunny • Humidity 48%', icon: '☀️', alert: 'Heat Wave Alert', advisoryTitle: 'Chilli Crop Prep', advisoryBody: 'Fallow fields should be plowed. Protect nursery beds with shading nets to prevent sun scorch.', advisoryIcon: '⚠️' },
    'Parvathipuram Manyam': { state: 'Andhra Pradesh', lat: 18.7770, lon: 83.4310, temp: '29°C', condition: 'Overcast • Humidity 85%', icon: '☁️', alert: 'Heavy Rain Warning', advisoryTitle: 'Maize Cultivation', advisoryBody: 'Provide ridges and furrows layout to drain excess rainwater from young maize plants.', advisoryIcon: '⚠️' },
    'Prakasam': { state: 'Andhra Pradesh', lat: 15.5057, lon: 80.0499, temp: '35°C', condition: 'Sunny • Humidity 50%', icon: '☀️', alert: 'Normal Weather', advisoryTitle: 'Pulse Crop Preparation', advisoryBody: 'Sow green gram or black gram seeds after pre-monsoon showers. Use trichoderma-treated seeds.', advisoryIcon: 'ℹ️' },
    'Sri Potti Sriramulu Nellore': { state: 'Andhra Pradesh', lat: 14.4426, lon: 79.9865, temp: '33°C', condition: 'Windy • Humidity 70%', icon: '💨', alert: 'High Winds Alert', advisoryTitle: 'Windbreak Protection', advisoryBody: 'High coastal winds forecast. Prop up young banana crops and protect nurseries from sand blasting.', advisoryIcon: '⚠️' },
    'Sri Sathya Sai': { state: 'Andhra Pradesh', lat: 14.1672, lon: 77.8105, temp: '37°C', condition: 'Sunny • Humidity 38%', icon: '☀️', alert: 'Dry Weather Warning', advisoryTitle: 'Groundnut Advisory', advisoryBody: 'Optimum sowing depth is 5cm. Ensure soil has sufficient moisture before seed broadcasting.', advisoryIcon: 'ℹ️' },
    'Srikakulam': { state: 'Andhra Pradesh', lat: 18.2949, lon: 83.8938, temp: '30°C', condition: 'Light Showers • Humidity 84%', icon: '🌦️', alert: 'Coastal Rain Warning', advisoryTitle: 'Cashew Orchards', advisoryBody: 'Clean orchard floor. Apply organic manure near canopy base. Spray neem oil to prevent tea mosquito bug.', advisoryIcon: 'ℹ️' },
    'Tirupati': { state: 'Andhra Pradesh', lat: 13.6288, lon: 79.4192, temp: '31°C', condition: 'Partly Cloudy • Humidity 62%', icon: '⛅', alert: 'Normal Weather', advisoryTitle: 'Land Preparation', advisoryBody: 'Favorable temperature. Proceed with land tilling and vermicompost mixing for vegetable crops.', advisoryIcon: 'ℹ️' },
    'Visakhapatnam': { state: 'Andhra Pradesh', lat: 17.6868, lon: 83.2185, temp: '30°C', condition: 'Overcast • Humidity 82%', icon: '🌧️', alert: 'Pre-Monsoon Alert', advisoryTitle: 'Kharif Sowing Window', advisoryBody: 'Light rains expected. Prepare paddy seed beds. Delay pesticide applications by 48 hours to avoid rain wash-off.', advisoryIcon: '⚠️' },
    'Vizianagaram': { state: 'Andhra Pradesh', lat: 18.1124, lon: 83.4027, temp: '31°C', condition: 'Partly Cloudy • Humidity 75%', icon: '⛅', alert: 'Normal Weather', advisoryTitle: 'Mesta Fiber Sowing', advisoryBody: 'Clean soil fields and prepare for Mesta seed sowing. Treat seeds with Azotobacter bio-fertilizer.', advisoryIcon: 'ℹ️' },
    'West Godavari': { state: 'Andhra Pradesh', lat: 16.5434, lon: 81.5224, temp: '32°C', condition: 'Humid • Humidity 83%', icon: '☁️', alert: 'Normal Weather', advisoryTitle: 'Fish Pond Advisory', advisoryBody: 'Maintain dissolved oxygen levels. Clean pond weeds. Avoid organic waste accumulation in summer heat.', advisoryIcon: 'ℹ️' },
    'YSR Kadapa': { state: 'Andhra Pradesh', lat: 14.4713, lon: 78.8220, temp: '37°C', condition: 'Sunny • Humidity 42%', icon: '☀️', alert: 'Dry Climate Warning', advisoryTitle: 'Banana Advisory', advisoryBody: 'Provide drip irrigation. Apply potash fertilizer to increase drought resistance in young plants.', advisoryIcon: 'ℹ️' },
    'Hyderabad': { state: 'Telangana', lat: 17.3850, lon: 78.4867, temp: '36°C', condition: 'Clear Sky • Humidity 42%', icon: '☀️', alert: 'High Heat Warning', advisoryTitle: 'Crop Hydration', advisoryBody: 'Warm conditions continue. Provide light, frequent irrigation to horticulture crops. Protect young saplings.', advisoryIcon: '🔥' },
    'Warangal': { state: 'Telangana', lat: 17.9689, lon: 79.5941, temp: '34°C', condition: 'Sunny • Humidity 55%', icon: '☀️', alert: 'Normal Weather', advisoryTitle: 'Paddy Sowing Alert', advisoryBody: 'Adequate canal water available. Sowing of short duration Paddy varieties is advised.', advisoryIcon: 'ℹ️' },
    'Khammam': { state: 'Telangana', lat: 17.2473, lon: 80.1514, temp: '35°C', condition: 'Cloudy • Humidity 60%', icon: '☁️', alert: 'Scattered Rains Alert', advisoryTitle: 'Cotton Sowing Prep', advisoryBody: 'Scattered light showers expected. Keep cotton sowing fields ready for immediate seeding post-rains.', advisoryIcon: 'ℹ️' },
    'Nizamabad': { state: 'Telangana', lat: 18.6725, lon: 78.0941, temp: '33°C', condition: 'Heavy Rain • Humidity 90%', icon: '🌧️', alert: 'Flash Flood Alert', advisoryTitle: 'Drainage Management', advisoryBody: 'Heavy rainfall in catchments. Clear drainage pathways in turmeric and soybean fields to prevent root rot.', advisoryIcon: '⚠️' },
    'Karimnagar': { state: 'Telangana', lat: 18.4386, lon: 79.1288, temp: '34°C', condition: 'Partly Cloudy • Humidity 58%', icon: '⛅', alert: 'Normal Weather', advisoryTitle: 'Maize Weeding Alert', advisoryBody: 'Dry spell suitable for manual or chemical weeding. Sowing of hybrid maize is recommended.', advisoryIcon: 'ℹ️' }
};

// Database mapping AP and TS Districts to Mandals / Sub-Districts
const MANDALS_DATABASE = {
    'Alluri Sitharama Raju': ['Addateegala', 'Ananthagiri', 'Araku Valley', 'Chintapalle', 'Chintur', 'Devipatnam', 'Dumbriguda', 'Etapaka', 'G. Madugula', 'Gangavaram', 'Gudem Kotha Veedhi', 'Gurthedu', 'Hukumpeta', 'Koyyuru', 'Kunavaram', 'Maredumilli', 'Munchingi Puttu', 'Paderu', 'Peda Bayalu', 'Rajavommangi', 'Rampachodavaram', 'Vararamachandrapuram', 'Y. Ramavaram'],
    'Anakapalli': ['Anakapalli', 'Atchutapuram', 'Butchayyapeta', 'Cheedikada', 'Chodavaram', 'Devarapalli', 'Elamanchili', 'Golugonda', 'K. Kotapadu', 'Kasimkota', 'Kotauratla', 'Madugula', 'Makavarapalem', 'Munagapaka', 'Nakkapalle', 'Narsipatnam', 'Nathavaram', 'Paravada', 'Payakaraopeta', 'Rambilli', 'Ravikamatham', 'Rolugunta', 'Sabbavaram', 'Sarvasiddhi Rayavaram'],
    'Ananthapuramu': ['Anantapuramu', 'Atmakur', 'Beluguppa', 'Bommanahal', 'Brahmasamudram', 'Bukkaraya Samudram', 'D.Hirehal', 'Garladinne', 'Gooty', 'Gummagatta', 'Guntakal', 'Kalyandurg', 'Kambadur', 'Kanekal', 'Kudair', 'Kundurpi', 'Narpala', 'Pamidi', 'Peddapappur', 'Peddavadugur', 'Putlur', 'Raptadu', 'Rayadurg', 'Settur', 'Singanamala', 'Tadipatri', 'Uravakonda', 'Vajrakarur', 'Vidapanakal', 'Yadiki', 'Yellanur'],
    'Annamayya': ['Beerangi Kothakota', 'Chinnamandyam', 'Chowdepalle', 'Galiveedu', 'Gurramkonda', 'Kalakada', 'Kalikiri', 'Kambhamvaripalle', 'Kurabalakota', 'Lakkireddipalli', 'Madanapalle', 'Mulakalacheruvu', 'Nimmanapalle', 'Peddamandyam', 'Peddathippasamudram', 'Pileru', 'Punganur', 'Ramapuram', 'Ramasamudram', 'Rayachoti', 'Sambepalli', 'Sodam', 'Somala', 'Thamballapalle', 'Vayalpad'],
    'Bapatla': ['Amruthalur', 'Bapatla', 'Bhattiprolu', 'Cherukupalle', 'Chinaganjam', 'Chirala', 'Inkollu', 'Karamchedu', 'Karlapalem', 'Kolluru', 'Martur', 'Nagaram', 'Nizampatnam', 'Parchur', 'Pittalavanipalem', 'Repalle', 'Tsundur', 'Vemuru', 'Vetapalem', 'Yeddanapudi'],
    'Chittoor': ['Baireddipalle', 'Bangarupalem', 'Chittoor', 'Chittoor Urban', 'Gangadhara Nellore', 'Gangavaram', 'Gudipala', 'Gudipalle', 'Irala', 'Karvetinagar', 'Kuppam', 'Nagari', 'Nindra', 'Palamaner', 'Palasamudram', 'Peddapanjani', 'Penumuru', 'Pulicherla', 'Puthalapattu', 'Ramakuppam', 'Rompicherla', 'Santhipuram', 'Sri Rangaraja Puram', 'Thavanampalle', 'Vedurukuppam', 'Venkatagirikota', 'Vijayapuram', 'Yadamarri'],
    'East Godavari': ['Anaparthi', 'Biccavolu', 'Chagallu', 'Devarapalle', 'Gokavaram', 'Gopalapuram', 'Kadiam', 'Kapileswarapuram', 'Korukonda', 'Kovvur', 'Mandapeta', 'Nallajerla', 'Nidadavole', 'Peravali', 'Rajahmundry Rural', 'Rajahmundry Urban', 'Rajanagaram', 'Rangampeta', 'Rayavaram', 'Seethanagaram', 'Tallapudi', 'Undrajavaram'],
    'Eluru': ['Agiripalli', 'Bhimadole', 'Buttayagudem', 'Chatrai', 'Chintalapudi', 'Denduluru', 'Dwaraka Tirumala', 'Eluru', 'Jangareddygudem', 'Jeelugu Milli', 'Kaikalur', 'Kalidindi', 'Kamavarapukota', 'Koyyalagudem', 'Kukunoor', 'Lingapalem', 'Mandavalli', 'Mudinepalle', 'Musunuru', 'Nidamarru', 'Nuzvid', 'Pedapadu', 'Pedavegi', 'Polavaram', 'T. Narasapuram', 'Unguturu', 'Velairpadu'],
    'Guntur': ['Chebrolu', 'Duggirala', 'Guntur East', 'Guntur West', 'Kakumanu', 'Kollipara', 'Mangalagiri', 'Medikonduru', 'Pedakakani', 'Pedanandipadu', 'Phirangipuram', 'Ponnur', 'Prathipadu', 'Tadepalli', 'Tadikonda', 'Tenali', 'Thullur', 'Vatticherukuru'],
    'Hyderabad': ['Amberpet', 'Asifnagar', 'Bahadurpura', 'Khairatabad', 'Musheerabad', 'Secunderabad'],
    'Kakinada': ['Gandepalle', 'Gollaprolu', 'Jaggampeta', 'Kajuluru', 'Kakinada Rural', 'Kakinada Urban', 'Karapa', 'Kirlampudi', 'Kotananduru', 'Kothapalle', 'Pedapudi', 'Peddapuram', 'Pithapuram', 'Prathipadu', 'Rowthulapudi', 'Samalkota', 'Sankhavaram', 'Thallarevu', 'Thondangi', 'Tuni', 'Yeleswaram'],
    'Karimnagar': ['Choppadandi', 'Gangadhara', 'Karimnagar', 'Manakondur'],
    'Khammam': ['Kallur', 'Khammam', 'Madhira', 'Nelakondapalli', 'Wyra'],
    'Konaseema': ['Ainavilli', 'Alamuru', 'Allavaram', 'Amalapuram', 'Ambajipeta', 'Atreyapuram', 'I. Polavaram', 'K. Gangavaram', 'Katrenikona', 'Kothapeta', 'Malikipuram', 'Mamidikuduru', 'Mummidivaram', 'P. Gannavaram', 'Ramachandrapuram', 'Ravulapalem', 'Razole', 'Sakhinetipalle', 'Uppalaguptam'],
    'Krishna': ['Avanigadda', 'Bantumilli', 'Bapulapadu', 'Challapalli', 'Gannavaram', 'Ghantasala', 'Gudivada', 'Gudlavalleru', 'Guduru', 'Kankipadu', 'Koduru', 'Kruthivennu', 'Machilipatnam', 'Mopidevi', 'Movva', 'Nagayalanka', 'Nandivada', 'Pamarru', 'Pamidimukkala', 'Pedana', 'Pedaparupudi', 'Penamaluru', 'Thotlavalluru', 'Unguturu', 'Vuyyuru'],
    'Kurnool': ['Adoni Rural', 'Adoni Urban', 'Alur', 'Aspari', 'C.Belagal', 'Chippagiri', 'Devanakonda', 'Gonegandla', 'Gudur', 'Halaharvi', 'Holagunda', 'Kallur', 'Kodumur', 'Kosigi', 'Kowthalam', 'Krishnagiri', 'Kurnool Rural', 'Kurnool Urban', 'Maddikera East', 'Mantralayam', 'Nandavaram', 'Orvakal', 'Pattikonda', 'Pedda Kadubur', 'Tuggali', 'Veldurthi', 'Yemmiganur'],
    'NTR': ['A. Konduru', 'Chandarlapadu', 'G.Konduru', 'Gampalagudem', 'Ibrahimpatnam', 'Jaggayyapeta', 'Kanchikacherla', 'Mylavaram', 'Nandigama', 'Penuganchiprolu', 'Reddigudem', 'Tiruvuru', 'Vatsavai', 'Veerullapadu', 'Vijayawada Central', 'Vijayawada East', 'Vijayawada North', 'Vijayawada Rural', 'Vijayawada West', 'Vissannapeta'],
    'Nandyal': ['Allagadda', 'Atmakur', 'Banaganapalle', 'Bandi Atmakur', 'Bethamcherla', 'Chagalamarri', 'Dhone', 'Dornipadu', 'Gadivemula', 'Gospadu', 'Jupadu Bungalow', 'Koilkuntla', 'Kolimigundla', 'Kothapalle', 'Mahanandi', 'Midthuru', 'Nandikotkur', 'Nandyal Rural', 'Nandyal Urban', 'Owk', 'Pagidyala', 'Pamulapadu', 'Panyam', 'Peapally', 'Rudravaram', 'Sanjamala', 'Sirivella', 'Srisailam', 'Uyyalawada', 'Velgodu'],
    'Nizamabad': ['Armoor', 'Bheemgal', 'Bodhan', 'Nizamabad'],
    'Palnadu': ['Amaravathi', 'Atchampet', 'Bellamkonda', 'Bollapalle', 'Chilakaluripet', 'Dachepalle', 'Durgi', 'Edlapadu', 'Gurazala', 'Ipuru', 'Karempudi', 'Krosuru', 'Machavaram', 'Macherla', 'Muppalla', 'Nadendla', 'Narasaraopet', 'Nekarikallu', 'Nuzendla', 'Pedakurapadu', 'Piduguralla', 'Rajupalem', 'Rentachintala', 'Rompicherla', 'Sattenapalle', 'Savalyapuram', 'Veldurthi', 'Vinukonda'],
    'Parvathipuram Manyam': ['Balijipeta', 'Bhamini', 'Garugubilli', 'Gummalakshmipuram', 'Jiyyammavalasa', 'Komarada', 'Kurupam', 'Makkuva', 'Pachipenta', 'Palakonda', 'Parvathipuram', 'Salur', 'Seethampeta', 'Seethanagaram', 'Veeraghattam'],
    'Prakasam': ['Addanki', 'Ardhaveedu', 'Ballikurava', 'Bestawaripeta', 'Chandra Sekhara Puram', 'Chimakurthi', 'Cumbum', 'Darsi', 'Donakonda Kanigiri', 'Dornala', 'Giddalur', 'Gudluru', 'Hanumanthuni Padu', 'J. Panguluru', 'Kandukuru', 'Kanigiri', 'Komarolu', 'Konakanamitla', 'Kondapi', 'Korisapadu', 'Kotha Patnam', 'Kurichedu', 'Lingasamudram', 'Maddipadu', 'Markapuram', 'Marripudi', 'Mundlamuru Ongole', 'Naguluppalapadu', 'Ongole Rural', 'Ongole Urban', 'Pamur', 'Peda Araveedu', 'Pedacherlo Palle', 'Podili', 'Ponnaluru', 'Pullalacheruvu', 'Racherla', 'Santhamaguluru', 'Santhanuthala Padu', 'Singarayakonda', 'Tangutur', 'Tarlupadu', 'Thallur', 'Tripuranthakam', 'Ulavapadu', 'Veligandla', 'Voletivaripalem', 'Yerragondapalem', 'Zarugumilli'],
    'Sri Potti Sriramulu Nellore': ['Allur', 'Ananthasagaram', 'Anumasamudrampeta', 'Atmakur', 'Bogolu', 'Buchireddypalem', 'Chejerla', 'Chillakur', 'Dagadarthi', 'Duttaluru', 'Gudur', 'Indukurpet', 'Jaladanki', 'Kaligiri', 'Kaluvoya', 'Kavali', 'Kodavaluru', 'Kota', 'Kovur', 'Manubolu', 'Marripadu', 'Muttukuru', 'Nellore Rural', 'Nellore Urban', 'Podalakuru', 'Rapuru', 'Saidapuramu', 'Sangam', 'Sitarampuramu', 'Thotapalligudur', 'Udayagiri', 'Venkatachalam', 'Vidavaluru', 'Vinjamuru'],
    'Sri Sathya Sai': ['Agali', 'Amadagur', 'Amarapuram', 'Bathalapalle', 'Bukkapatnam', 'Chennekothapalle', 'Chilamathur', 'Dharmavaram', 'Gandlapenta', 'Gorantla', 'Gudibanda', 'Hindupur', 'Kadiri', 'Kanaganapalle', 'Kothacheruvu', 'Lepakshi', 'Madakasira', 'Mudigubba', 'Nallacheruvu', 'Nallamada', 'Nambulapulakunta', 'Obuladevaracheruvu', 'Parigi', 'Penukonda', 'Puttaparthi', 'Ramagiri', 'Roddam', 'Rolla', 'Somandepalle', 'Tadimarri', 'Talupula', 'Tanakal'],
    'Srikakulam': ['Amadalavalasa', 'Burja', 'Etcherla', 'Ganguvarisigadam', 'Gara', 'Hiraam', 'Ichchapuram', 'Jalumuru', 'Kanchili', 'Kaviti', 'Kotabommali', 'Kothuru', 'Lakshminarsupeta', 'Laveru', 'Mandasa', 'Meliaputti', 'Nandigam', 'Narasannapeta', 'Palasa', 'Pathapatnam', 'Polaki', 'Ponduru', 'Ranastalam', 'Santhabommali', 'Saravakota', 'Sarubujjili', 'Sompeta', 'Srikakulam', 'Tekkali', 'Vajrapukothuru'],
    'Tirupati': ['Balayapalle', 'Buchinaidu Kandriga', 'Chandragiri', 'Chinnagottigallu', 'Chittamur', 'Chitvel', 'Dakkili', 'Doravarisatram', 'K. V. B. Puram', 'Kodur', 'Nagalapuram', 'Naidupeta', 'Narayanavanam', 'Obulavaripalle', 'Ozili', 'Pakala', 'Pellakur', 'Penagalur', 'Pichatur', 'Pullampeta', 'Puttur', 'Ramachandrapuram', 'Renigunta', 'Satyavedu', 'Srikalahasti', 'Sullurpeta', 'Tada', 'Thottambedu', 'Tirupati Rural', 'Tirupati Urban', 'Vadamalapeta', 'Vakadu', 'Varadaiahpalem', 'Venkatagiri', 'Yerpedu', 'Yerravaripalem'],
    'Visakhapatnam': ['Anandapuram', 'Bheemunipatnam', 'Gajuwaka', 'Gopalapatnam', 'Maharanipeta', 'Mulagada', 'Padmanabham', 'Pedagantyada', 'Pendurthi', 'Seethammadhara', 'Visakhapatnam Rural'],
    'Vizianagaram': ['Badangi', 'Bhogapuram', 'Bobbili', 'Bondapalle', 'Cheepurupalle', 'Dattirajeru', 'Denkada', 'Gajapathinagaram', 'Gantyada', 'Garividi', 'Gurla', 'Jami', 'Kothavalasa', 'Lakkavarapukota', 'Mentada', 'Merakamudidam', 'Nellimarla', 'Pusapatirega', 'Rajam', 'Ramabhadrapuram', 'Regidi Amadalavalasa', 'Santhakaviti', 'Srungavarapukota', 'Therlam', 'Vangara', 'Vepada', 'Vizianagaram'],
    'Warangal': ['Dharmasagar', 'Geesugonda', 'Hanamkonda', 'Hasanparthy', 'Warangal'],
    'West Godavari': ['Achanta', 'Akividu', 'Attili', 'Bhimavaram', 'Ganapavaram', 'Iragavaram', 'Kalla', 'Mogalthur', 'Palacoderu', 'Palakollu', 'Pentapadu', 'Penugonda', 'Penumantra', 'Poduru', 'Tadepalligudem', 'Tanuku', 'Undi', 'Veeravasaram', 'Yelamanchili'],
    'YSR Kadapa': ['Atlur', 'B. Kodur', 'Badvel', 'Brahmamgarimattam', 'Chakrayapet', 'Chapad', 'Chennur', 'Chinthakommadinne', 'Duvvur', 'Gopavaram', 'Jammalamadugu', 'Kadapa', 'Kalasapadu', 'Kamalapuram', 'Khajipet', 'Kondapuram', 'Lingala', 'Muddanur', 'Mylavaram', 'Nandalur', 'Peddamudium', 'Pendlimarri', 'Porumamilla', 'Proddatur', 'Pulivendla', 'Rajampet', 'Rajupalem', 'S.Mydukur', 'Sidhout', 'Simhadripuram', 'Sri Avadhutha Kasinayana', 'T. Sundupalle', 'Thondur', 'Vallur', 'Veeraballi', 'Veerapunayunipalle', 'Vempalle', 'Vemula', 'Vontimitta', 'Yerraguntla'],
};

function onDistrictChange() {
    const districtSelect = document.getElementById('reg-region');
    const mandalGroup = document.getElementById('reg-mandal-group');
    const mandalSelect = document.getElementById('reg-mandal');
    
    if (!districtSelect || !mandalSelect || !mandalGroup) return;
    
    const selectedDistrict = districtSelect.value;
    const mandals = MANDALS_DATABASE[selectedDistrict];
    
    if (mandals && mandals.length > 0) {
        mandalSelect.innerHTML = '';
        mandals.forEach(mandal => {
            const option = document.createElement('option');
            option.value = mandal;
            option.textContent = mandal;
            mandalSelect.appendChild(option);
        });
        mandalGroup.style.display = 'block';
    } else {
        mandalSelect.innerHTML = '';
        mandalGroup.style.display = 'none';
    }
}

// AI Doctor Specimen Diagnoses
const SPECIMENS = {
    'blast': {
        disease: 'Rice Leaf Blast (Fungal)',
        severity: 'Critical / High Severity',
        severityClass: 'badge-danger',
        confidence: '97%',
        emoticon: '🍂',
        symptoms: 'Caused by Pyricularia oryzae fungus. Spindle-shaped lesions with grayish centers and brown borders. Rapidly damages leaves, nodes, and panicles, leading to lodging and zero grain fill.',
        organic: 'Apply Pseudomonas fluorescens biological powder at 10g/L. Keep soil moist but drain stagnant water. Avoid excessive nitrogen fertilizer.',
        chemical: 'Spray Tricyclazole 75% WP at 0.6g per Litre of water OR Isoprothiolane 40% EC at 1.5ml per Litre immediately.',
        tip: 'Tip: Grow blast-resistant varieties in the future. Clean farm equipment to limit spores.'
    },
    'blight': {
        disease: 'Cotton Leaf Curl Virus (CLCuV)',
        severity: 'Moderate Severity',
        severityClass: 'badge',
        confidence: '92%',
        emoticon: '🍁',
        symptoms: 'Transmitted by Silverfly (Whiteflies). Upward or downward curling of leaf margins, thick veins, and plant stunting. Reduces boll formation and lint quality.',
        organic: 'Spray Neem oil formulation (1500 ppm) at 5ml/L of water. Install yellow sticky traps (10 per acre) to control whitefly vector population.',
        chemical: 'Apply Imidacloprid 17.8% SL at 0.3ml per Litre of water OR Acetamiprid 20% SP at 0.2g per Litre to target whiteflies.',
        tip: 'Tip: Eradicate weed hosts near field boundaries. Avoid spraying broad-spectrum pyrethroids.'
    },
    'healthy': {
        disease: 'Healthy Specimen - Soya Crop',
        severity: 'Perfect Health',
        severityClass: 'badge-success',
        confidence: '99%',
        emoticon: '🍃',
        symptoms: 'Leaves are vibrant green, free of physical lesions, insect chew-marks, or discoloration. Photosynthetic activity is optimum. Strong vegetative nodes.',
        organic: 'Maintain crop health with dynamic vermicompost liquid fertilizer. Spray general organic growth boosters (Panchagavya at 3%).',
        chemical: 'No chemical inputs necessary. Practice micro-irrigation and weed management to maintain health.',
        tip: 'Tip: Great job! Continue monitoring for any early signs of pests weekly.'
    }
};

// --- APPLICATION STATE CONTAINER ---
let AppState = {
    user: null, // Holds profile once logged in
    cart: [],
    customSellerListings: [],
    customLaborRequests: [],
    activeTradeTab: 'buy',
    activeLaborTab: 'hire',
    selectedSpecimen: null,
    uploadedImageBase64: null
};

// --- CORE UTILITIES ---
function showToast(text, type = 'success') {
    const toast = document.getElementById('toast-message');
    toast.textContent = text;
    if (type === 'error') {
        toast.style.background = '#dc2626';
    } else {
        toast.style.background = '#1e293b';
    }
    toast.classList.add('show');
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// Format local date
function getFormattedDate() {
    const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const d = new Date();
    return `${days[d.getDay()]}, ${months[d.getMonth()]} ${d.getDate()}, ${d.getFullYear()}`;
}

// --- PERSISTENCE AND ROUTER ---
function initApp() {
    // Check if user is cached in session storage (logs out on tab close)
    const cachedUser = sessionStorage.getItem('kisan_mitra_user');
    const cachedCart = localStorage.getItem('kisan_mitra_cart');
    const cachedListings = localStorage.getItem('kisan_mitra_listings');
    const cachedRequests = localStorage.getItem('kisan_mitra_labor');

    if (cachedUser) {
        AppState.user = JSON.parse(cachedUser);
    }
    if (cachedCart) {
        AppState.cart = JSON.parse(cachedCart);
    }
    if (cachedListings) {
        AppState.customSellerListings = JSON.parse(cachedListings);
    }
    if (cachedRequests) {
        AppState.customLaborRequests = JSON.parse(cachedRequests);
    }

    // Populate regions dropdown dynamics
    populateRegionsDropdown();
    populateMandiDistrictsDropdown();
    onDistrictChange();

    // Bind Auth Submit Events
    document.getElementById('login-form').addEventListener('submit', handleLoginSubmit);
    document.getElementById('register-form').addEventListener('submit', handleRegisterSubmit);
    document.getElementById('logout-btn').addEventListener('click', handleLogout);

    // Bind dropdown change event
    document.getElementById('reg-region').addEventListener('change', onDistrictChange);

    // Bind Top Right header buttons
    document.getElementById('auth-toggle-header-btn').addEventListener('click', handleHeaderAuthClick);

    // Bind GPS tracking buttons
    document.getElementById('gps-register-btn').addEventListener('click', () => detectGPSLocation(false));
    document.getElementById('gps-dashboard-btn').addEventListener('click', () => detectGPSLocation(true));

    // Bind Toggle links
    document.getElementById('to-register').addEventListener('click', () => {
        document.getElementById('login-card').style.display = 'none';
        document.getElementById('register-card').style.display = 'block';
        document.getElementById('auth-toggle-header-btn').textContent = 'Login';
    });
    document.getElementById('to-login').addEventListener('click', () => {
        document.getElementById('register-card').style.display = 'none';
        document.getElementById('login-card').style.display = 'block';
        document.getElementById('auth-toggle-header-btn').textContent = 'Register';
    });

    if (AppState.user) {
        setupAuthenticatedUI();
    } else {
        setupGuestUI();
    }
    navigateTo('home');
    updateCartCountBadge();
}

function populateRegionsDropdown() {
    const dropdown = document.getElementById('reg-region');
    if (!dropdown) return;
    dropdown.innerHTML = '';
    
    // Sort locations alphabetically
    const keys = Object.keys(LOCATION_DATABASE).sort();
    
    keys.forEach(key => {
        const option = document.createElement('option');
        option.value = key;
        option.textContent = `${key} (${LOCATION_DATABASE[key].state})`;
        dropdown.appendChild(option);
    });
}

function handleHeaderAuthClick() {
    const activeScreen = document.querySelector('.app-screen.active');
    
    if (activeScreen && activeScreen.id === 'screen-auth') {
        navigateTo('home');
    } else {
        // Toggle forms state to login card default
        document.getElementById('login-card').style.display = 'block';
        document.getElementById('register-card').style.display = 'none';
        navigateTo('auth');
    }
}

function toggleGuestForms() {
    const loginCard = document.getElementById('login-card');
    const registerCard = document.getElementById('register-card');
    const btn = document.getElementById('auth-toggle-header-btn');
    
    if (loginCard.style.display === 'none') {
        loginCard.style.display = 'block';
        registerCard.style.display = 'none';
        btn.textContent = 'Register';
    } else {
        loginCard.style.display = 'none';
        registerCard.style.display = 'block';
        btn.textContent = 'Login';
    }
}

function setupAuthenticatedUI() {
    // Hide auth screen
    document.getElementById('screen-auth').style.display = 'none';
    document.getElementById('screen-auth').classList.remove('active');
    
    // Show header in profile mode, hide guest mode
    document.getElementById('app-header').style.display = 'flex';
    document.getElementById('auth-toggle-header-btn').style.display = 'none';
    document.getElementById('profile-container').style.display = 'flex';
    const bNav = document.getElementById('app-bottom-nav'); if (bNav) bNav.style.display = 'flex';
    
    // Fill dynamic header elements
    document.getElementById('header-username').textContent = AppState.user.name;
    document.getElementById('header-avatar').textContent = AppState.user.name.charAt(0).toUpperCase();
    
    // Load dashboard
    updateDashboardUI();
}

function setupGuestUI() {
    // Show header in guest button mode, hide profile mode
    document.getElementById('app-header').style.display = 'flex';
    document.getElementById('auth-toggle-header-btn').style.display = 'block';
    document.getElementById('auth-toggle-header-btn').textContent = 'Login / Register';
    document.getElementById('profile-container').style.display = 'none';
    const bNav = document.getElementById('app-bottom-nav'); if (bNav) bNav.style.display = 'flex';
    
    // Show home screen stats
    updateDashboardUI();
}

// Navigation router
function navigateTo(screenId) {
    if (screenId === 'nav-doctor') screenId = 'doctor';
    
    // Deactivate all screens
    const screens = document.querySelectorAll('.app-screen');
    screens.forEach(s => {
        s.style.display = 'none';
        s.classList.remove('active');
    });

    // Activate selected screen
    const targetScreen = document.getElementById(`screen-${screenId}`);
    if (targetScreen) {
        targetScreen.style.display = 'block';
        targetScreen.classList.add('active');
    }

    // Update bottom nav highlighting
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(nav => nav.classList.remove('active'));
    
    const activeNav = document.getElementById(`nav-${screenId}`);
    if (activeNav) {
        activeNav.classList.add('active');
    }
    
    // Update top nav highlighting
    const topNavLinks = document.querySelectorAll('.top-nav-link');
    topNavLinks.forEach(nav => nav.classList.remove('active'));
    
    const activeTopNav = document.getElementById(`top-nav-${screenId}`);
    if (activeTopNav) {
        activeTopNav.classList.add('active');
    }

    // Update guest header button label based on screen
    const guestBtn = document.getElementById('auth-toggle-header-btn');
    if (guestBtn && !AppState.user) {
        if (screenId === 'auth') {
            guestBtn.textContent = 'Home 🌾';
            guestBtn.style.background = 'transparent';
            guestBtn.style.border = '2px solid rgba(255, 255, 255, 0.4)';
            guestBtn.style.boxShadow = 'none';
        } else {
            guestBtn.textContent = 'Login / Register';
            guestBtn.style.background = '';
            guestBtn.style.border = '';
            guestBtn.style.boxShadow = '';
        }
    }

    // Trigger sub-app render actions
    if (screenId === 'trade') {
        renderAgriTrade();
    } else if (screenId === 'labor') {
        renderLaborForce();
    } else if (screenId === 'mandis') {
        renderMandiRates();
    } else if (screenId === 'home') {
        updateDashboardUI();
    }
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// --- AUTH HANDLERS ---
function handleLoginSubmit(e) {
    const phone = document.getElementById('login-phone').value.trim();
    const pin = document.getElementById('login-pin').value.trim();

    // Check if registered user exists in localstorage
    const registeredUser = localStorage.getItem(`km_reg_profile_${phone}`);
    if (registeredUser) {
        const userObj = JSON.parse(registeredUser);
        if (userObj.pin === pin) {
            AppState.user = userObj;
            sessionStorage.setItem('kisan_mitra_user', JSON.stringify(userObj));
            showToast(`Welcome back, ${userObj.name}!`);
            setupAuthenticatedUI();
        } else {
            showToast('Invalid Secure PIN. Please try again.', 'error');
        }
    } else {
        // Mock fallback check for default demo login
        if (phone === '9999999999' && pin === '1234') {
            const defaultUser = { name: 'Jeevan', phone: '9999999999', region: 'Visakhapatnam', pin: '1234' };
            AppState.user = defaultUser;
            sessionStorage.setItem('kisan_mitra_user', JSON.stringify(defaultUser));
            showToast('Welcome back, Jeevan (Demo Account)!');
            setupAuthenticatedUI();
        } else {
            showToast('User not found. Please register first.', 'error');
        }
    }
}

function handleRegisterSubmit(e) {
    const name = document.getElementById('reg-name').value.trim();
    const phone = document.getElementById('reg-phone').value.trim();
    const region = document.getElementById('reg-region').value;
    const mandal = document.getElementById('reg-mandal').value;
    const pin = document.getElementById('reg-pin').value.trim();

    if (phone.length < 10) {
        showToast('Please enter a valid 10-digit mobile number.', 'error');
        return;
    }
    if (pin.length !== 4 || isNaN(pin)) {
        showToast('PIN must be a 4-digit number.', 'error');
        return;
    }

    const newUser = { name, phone, region, mandal, pin };
    // Save to all registered accounts storage
    localStorage.setItem(`km_reg_profile_${phone}`, JSON.stringify(newUser));
    
    // Log user in automatically
    AppState.user = newUser;
    sessionStorage.setItem('kisan_mitra_user', JSON.stringify(newUser));

    showToast('Registration successful! Welcome to Kisan Mitra.');
    setupAuthenticatedUI();
    
    // Reset forms
    document.getElementById('register-form').reset();
}

function handleLogout() {
    AppState.user = null;
    AppState.cart = [];
    sessionStorage.removeItem('kisan_mitra_user');
    localStorage.removeItem('kisan_mitra_cart');
    showToast('Logged out successfully.');
    setupGuestUI();
    navigateTo('home');
}


// --- HOME DASHBOARD ENGINE ---
function updateDashboardUI() {
    const isLoggedIn = AppState.user !== null;
    const region = isLoggedIn ? AppState.user.region : (document.getElementById('reg-region')?.value || 'Visakhapatnam');
    const weather = LOCATION_DATABASE[region] || LOCATION_DATABASE['Visakhapatnam'];
    
    // Dynamic greeting based on time of day
    const hour = new Date().getHours();
    let greet = 'Welcome';
    if (hour < 12) greet = 'Good Morning';
    else if (hour < 17) greet = 'Good Afternoon';
    else greet = 'Good Evening';

    document.getElementById('hero-date-text').textContent = getFormattedDate();
    
    const userNameSpan = document.getElementById('dash-username');
    if (isLoggedIn) {
        userNameSpan.textContent = AppState.user.name;
    } else {
        userNameSpan.textContent = 'Guest Farmer';
    }
    
    const mandalText = isLoggedIn ? (AppState.user.mandal ? ` (${AppState.user.mandal} Mandal)` : '') : '';
    const stateSuffix = LOCATION_DATABASE[region] ? (LOCATION_DATABASE[region].state === 'Telangana' ? 'TS' : 'AP') : 'AP';
    document.getElementById('dash-location').textContent = `${region}${mandalText}, ${stateSuffix}`;
    
    document.getElementById('dash-temp').textContent = weather.temp;
    document.getElementById('dash-weather-condition').textContent = weather.condition;
    document.getElementById('dash-weather-icon').textContent = weather.icon;
    document.getElementById('dash-alert-tag').textContent = weather.alert;

    // Advisory panel updates
    document.getElementById('advisory-icon').textContent = weather.advisoryIcon;
    document.getElementById('advisory-title').textContent = weather.advisoryTitle;
    document.getElementById('advisory-body').innerHTML = weather.advisoryBody;
}


// --- AGRI-TRADE MARKETPLACE ENGINE ---
function switchTradeTab(tab) {
    AppState.activeTradeTab = tab;
    
    const buyBtn = document.getElementById('tab-trade-buy');
    const sellBtn = document.getElementById('tab-trade-sell');
    const buyContent = document.getElementById('trade-buy-content');
    const sellContent = document.getElementById('trade-sell-content');

    if (tab === 'buy') {
        buyBtn.classList.add('active');
        sellBtn.classList.remove('active');
        buyContent.style.display = 'block';
        sellContent.style.display = 'none';
        renderAgriTradeCatalog(CROP_CATALOG);
    } else {
        buyBtn.classList.remove('active');
        sellBtn.classList.add('active');
        buyContent.style.display = 'none';
        sellContent.style.display = 'block';
        renderSellerListings();
    }
}

function renderAgriTrade() {
    switchTradeTab(AppState.activeTradeTab);
}

function renderAgriTradeCatalog(items) {
    const grid = document.getElementById('catalog-grid');
    grid.innerHTML = '';

    if (items.length === 0) {
        grid.innerHTML = '<p style="grid-column: 1/-1; text-align: center; padding: 20px; color: var(--text-muted);">No products found matching your search.</p>';
        return;
    }

    items.forEach(product => {
        const card = document.createElement('div');
        card.className = 'product-card';
        card.innerHTML = `
            <div>
                <div class="product-img">${product.img}</div>
                <h4 class="product-title">${product.name}</h4>
                <p class="product-desc">${product.desc}</p>
            </div>
            <div>
                <div style="font-size: 11px; color: var(--text-muted); margin-bottom: 8px;">Unit: ${product.unit}</div>
                <div class="product-meta">
                    <span class="price-tag">₹${product.price}</span>
                    <button class="btn btn-small" onclick="addToCart('${product.id}')">Add +</button>
                </div>
            </div>
        `;
        grid.appendChild(card);
    });
}

function filterBuyCatalog() {
    const query = document.getElementById('buy-search').value.toLowerCase();
    const filtered = CROP_CATALOG.filter(item => 
        item.name.toLowerCase().includes(query) || 
        item.desc.toLowerCase().includes(query)
    );
    renderAgriTradeCatalog(filtered);
}

// Seller postings
function triggerMockFileSelect() {
    document.getElementById('sell-crop-photo').click();
}

function previewCropImage(input) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            AppState.uploadedImageBase64 = e.target.result;
            document.getElementById('photo-upload-label').textContent = 'Image Attached Successfully!';
            document.getElementById('photo-upload-label').style.color = 'var(--primary)';
        };
        reader.readAsDataURL(input.files[0]);
    }
}

function publishCropSale() {
    if (!AppState.user) {
        showToast('Please login to publish crop listings.', 'error');
        navigateTo('auth');
        return;
    }
    const cropName = document.getElementById('sell-crop-name').value.trim();
    const quantity = parseInt(document.getElementById('sell-quantity').value);
    const price = parseInt(document.getElementById('sell-price').value);

    if (!cropName || isNaN(quantity) || isNaN(price)) {
        showToast('Please fill all required fields correctly.', 'error');
        return;
    }

    const newListing = {
        id: 'user-lst-' + Date.now(),
        farmer: AppState.user.name,
        crop: cropName,
        quantity: quantity,
        price: price,
        district: AppState.user.region,
        phone: AppState.user.phone,
        img: AppState.uploadedImageBase64 || '🌾',
        date: new Date().toISOString().split('T')[0]
    };

    AppState.customSellerListings.unshift(newListing);
    localStorage.setItem('kisan_mitra_listings', JSON.stringify(AppState.customSellerListings));

    showToast('Crop listing published successfully!');
    
    // Reset form & preview
    document.getElementById('sell-crop-form').reset();
    document.getElementById('photo-upload-label').textContent = 'Click to upload crop photograph';
    document.getElementById('photo-upload-label').style.color = '';
    AppState.uploadedImageBase64 = null;

    renderSellerListings();
}

function renderSellerListings() {
    const grid = document.getElementById('listings-grid');
    grid.innerHTML = '';

    const allListings = [...AppState.customSellerListings, ...DEFAULT_TRADE_LISTINGS];

    allListings.forEach(item => {
        const isCustomPhoto = item.img.startsWith('data:image');
        const imgContent = isCustomPhoto 
            ? `<img src="${item.img}" style="width:100%; height:100%; object-fit:cover;" />` 
            : item.img;

        const card = document.createElement('div');
        card.className = 'product-card';
        card.innerHTML = `
            <div>
                <div class="product-img">${imgContent}</div>
                <h4 class="product-title">${item.crop}</h4>
                <p class="product-desc" style="margin-bottom: 8px;">
                    <strong>Quantity:</strong> ${item.quantity} Quintals<br>
                    <strong>Farmer:</strong> ${item.farmer}<br>
                    <strong>Mandi Yard:</strong> ${item.district}
                </p>
            </div>
            <div>
                <div class="product-meta">
                    <span class="price-tag" style="background:#fef9c3; color:var(--secondary)">₹${item.price}/Qtl</span>
                    <a href="tel:${item.phone}" class="btn btn-small btn-gold" style="text-decoration:none;">📞 Call</a>
                </div>
            </div>
        `;
        grid.appendChild(card);
    });
}


// --- INTERACTIVE CART ENGINE ---
function updateCartCountBadge() {
    const badge = document.getElementById('cart-item-count');
    const totalCount = AppState.cart.reduce((sum, item) => sum + item.quantity, 0);
    
    if (totalCount > 0) {
        badge.textContent = totalCount;
        badge.style.display = 'flex';
    } else {
        badge.style.display = 'none';
    }
}

function addToCart(productId) {
    const product = CROP_CATALOG.find(item => item.id === productId);
    if (!product) return;

    const existing = AppState.cart.find(item => item.productId === productId);
    if (existing) {
        existing.quantity += 1;
    } else {
        AppState.cart.push({
            productId: product.id,
            name: product.name,
            price: product.price,
            img: product.img,
            quantity: 1
        });
    }

    localStorage.setItem('kisan_mitra_cart', JSON.stringify(AppState.cart));
    updateCartCountBadge();
    showToast(`Added ${product.name} to cart.`);
}

function openCart() {
    const overlay = document.getElementById('cart-overlay-element');
    const drawer = document.getElementById('cart-drawer-element');
    
    renderCartItems();
    
    overlay.classList.add('active');
    drawer.classList.add('active');
}

function closeCart() {
    const overlay = document.getElementById('cart-overlay-element');
    const drawer = document.getElementById('cart-drawer-element');
    
    overlay.classList.remove('active');
    drawer.classList.remove('active');
}

function renderCartItems() {
    const container = document.getElementById('cart-items-container');
    const totalLabel = document.getElementById('cart-total-price');
    const emptyText = document.getElementById('cart-empty-text');

    container.innerHTML = '';

    if (AppState.cart.length === 0) {
        container.appendChild(emptyText);
        emptyText.style.display = 'block';
        totalLabel.textContent = '₹0';
        return;
    }

    emptyText.style.display = 'none';
    let totalSum = 0;

    AppState.cart.forEach(item => {
        totalSum += item.price * item.quantity;
        
        const itemRow = document.createElement('div');
        itemRow.className = 'cart-item';
        itemRow.innerHTML = `
            <div class="cart-item-img">${item.img}</div>
            <div class="cart-item-info">
                <h4 style="font-size: 13px; font-weight:700;">${item.name}</h4>
                <p style="font-size: 12px; color: var(--text-muted); margin-top: 4px;">₹${item.price} x ${item.quantity}</p>
            </div>
            <div style="display:flex; flex-direction:column; align-items:flex-end; gap:6px;">
                <span style="font-weight:700; font-size:14px;">₹${item.price * item.quantity}</span>
                <span style="font-size:11px; color:var(--danger); cursor:pointer; font-weight:700;" onclick="removeFromCart('${item.productId}')">Delete</span>
            </div>
        `;
        container.appendChild(itemRow);
    });

    totalLabel.textContent = `₹${totalSum}`;
}

function removeFromCart(productId) {
    AppState.cart = AppState.cart.filter(item => item.productId !== productId);
    localStorage.setItem('kisan_mitra_cart', JSON.stringify(AppState.cart));
    updateCartCountBadge();
    renderCartItems();
}

function checkoutCart() {
    if (!AppState.user) {
        showToast('Please login to place an order.', 'error');
        closeCart();
        navigateTo('auth');
        return;
    }
    if (AppState.cart.length === 0) {
        showToast('Your cart is empty!', 'error');
        return;
    }
    
    // Simulate successful checkout
    AppState.cart = [];
    localStorage.removeItem('kisan_mitra_cart');
    updateCartCountBadge();
    closeCart();
    
    // Checkout confirmation popup
    alert('🎉 Order Placed Successfully!\nYour agricultural supplies will be shipped to your registered district. Payment can be done Cash-on-Delivery (COD).');
    showToast('Order created successfully!');
}


// --- LABOR FORCE ENGINE ---
function switchLaborTab(tab) {
    AppState.activeLaborTab = tab;
    
    const hireBtn = document.getElementById('tab-labor-hire');
    const postBtn = document.getElementById('tab-labor-post');
    const hireContent = document.getElementById('labor-hire-content');
    const postContent = document.getElementById('labor-post-content');

    if (tab === 'hire') {
        hireBtn.classList.add('active');
        postBtn.classList.remove('active');
        hireContent.style.display = 'block';
        postContent.style.display = 'none';
        renderLaborTeamsList(MOCK_LABOR_TEAMS);
    } else {
        hireBtn.classList.remove('active');
        postBtn.classList.add('active');
        hireContent.style.display = 'none';
        postContent.style.display = 'block';
        renderLaborRequests();
    }
}

function renderLaborForce() {
    switchLaborTab(AppState.activeLaborTab);
}

function renderLaborTeamsList(teams) {
    const list = document.getElementById('labor-teams-list');
    list.innerHTML = '';

    if (teams.length === 0) {
        list.innerHTML = '<p style="text-align:center; padding: 20px; color: var(--text-muted);">No teams found for the filter.</p>';
        return;
    }

    teams.forEach(team => {
        const card = document.createElement('div');
        card.className = 'labor-card';
        card.innerHTML = `
            <div class="labor-header">
                <div>
                    <h4 style="font-size:16px; font-weight:800; color:var(--text-main);">${team.leader} Crew</h4>
                    <span class="badge badge-success" style="margin-top:6px;">${team.specialization} Speciality</span>
                </div>
                <div class="labor-rating">
                    <span>★</span> <span>${team.rating}</span>
                </div>
            </div>
            <div style="display:flex; justify-content:space-between; align-items:center; margin-top:14px; border-top:1px solid #f1f5f9; padding-top:12px;">
                <div class="labor-details">
                    <span>👥 <strong>Crew Size:</strong> ${team.size} Workers</span>
                    <span>📍 <strong>Location:</strong> ${team.location} District</span>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:14px; font-weight:800; color:var(--secondary);">₹${team.rate}/Day</div>
                    <button class="btn btn-small btn-earth" onclick="requestLaborCall('${team.leader}', '${team.contact}')" style="margin-top:8px;">Request Call</button>
                </div>
            </div>
        `;
        list.appendChild(card);
    });
}

function filterLaborTeams() {
    const taskType = document.getElementById('labor-filter-type').value;
    if (taskType === 'all') {
        renderLaborTeamsList(MOCK_LABOR_TEAMS);
    } else {
        const filtered = MOCK_LABOR_TEAMS.filter(t => t.specialization === taskType);
        renderLaborTeamsList(filtered);
    }
}

function requestLaborCall(leader, phone) {
    if (!AppState.user) {
        showToast('Please login to request labor callbacks.', 'error');
        navigateTo('auth');
        return;
    }
    alert(`📞 Call Requested!\nWe have sent your contact number (${AppState.user.phone}) to ${leader} Crew. They will call you shortly to discuss rates and dates.`);
    showToast(`Call requested from ${leader}.`);
}

function publishLaborRequest() {
    if (!AppState.user) {
        showToast('Please login to broadcast labor requests.', 'error');
        navigateTo('auth');
        return;
    }
    const task = document.getElementById('labor-job-type').value;
    const workers = parseInt(document.getElementById('labor-crew-size').value);
    const wage = parseInt(document.getElementById('labor-daily-wage').value);
    const date = document.getElementById('labor-start-date').value;

    if (isNaN(workers) || isNaN(wage) || !date) {
        showToast('Please fill all fields correctly.', 'error');
        return;
    }

    const newRequest = {
        id: 'lab-req-' + Date.now(),
        task: task,
        workers: workers,
        wage: wage,
        date: date,
        phone: AppState.user.phone,
        status: 'Active Broadcasting'
    };

    AppState.customLaborRequests.unshift(newRequest);
    localStorage.setItem('kisan_mitra_labor', JSON.stringify(AppState.customLaborRequests));

    showToast('Labor broadcast successfully published!');
    document.getElementById('post-labor-form').reset();
    renderLaborRequests();
}

function renderLaborRequests() {
    const container = document.getElementById('labor-requests-list');
    container.innerHTML = '';

    if (AppState.customLaborRequests.length === 0) {
        container.innerHTML = '<p style="text-align:center; padding: 20px; color: var(--text-muted); font-size:13px;">No active requests. Publish one above.</p>';
        return;
    }

    AppState.customLaborRequests.forEach(req => {
        const card = document.createElement('div');
        card.className = 'labor-card';
        card.innerHTML = `
            <div style="display:flex; justify-content:space-between; align-items:start;">
                <div>
                    <h4 style="font-size:15px; font-weight:800; color:var(--secondary);">${req.task}</h4>
                    <p style="font-size:12px; color:var(--text-muted); margin-top:4px;">Required From: <strong>${req.date}</strong></p>
                </div>
                <span class="badge badge-blue">${req.status}</span>
            </div>
            <div style="display:flex; justify-content:space-between; align-items:center; margin-top:14px; border-top:1px solid #f1f5f9; padding-top:12px;">
                <div class="labor-details">
                    <span>👥 <strong>Workers Needed:</strong> ${req.workers}</span>
                    <span>💰 <strong>Offered wage:</strong> ₹${req.wage}/Day</span>
                </div>
                <button class="btn btn-small btn-danger" onclick="deleteLaborRequest('${req.id}')">Stop</button>
            </div>
        `;
        container.appendChild(card);
    });
}

function deleteLaborRequest(id) {
    AppState.customLaborRequests = AppState.customLaborRequests.filter(req => req.id !== id);
    localStorage.setItem('kisan_mitra_labor', JSON.stringify(AppState.customLaborRequests));
    showToast('Labor request deleted.');
    renderLaborRequests();
}


// --- AP LIVE MANDIS ENGINE ---
function renderMandiRates() {
    const crop = document.getElementById('mandi-filter-crop').value;
    const district = document.getElementById('mandi-filter-district').value;
    
    // Update chart title
    document.getElementById('mandi-chart-title').textContent = `Weekly Price Trend (${crop})`;

    // Render Trend Graph
    renderTrendGraph(crop);

    // Render rates list
    const ratesList = document.getElementById('mandi-rates-list');
    ratesList.innerHTML = '';

    let listData = MOCK_MANDI_DATABASE[crop] || [];
    
    // Generate realistic mandi rates for any district that lacks hardcoded mock entries
    if (district !== 'all') {
        const districtHasData = listData.some(d => d.district === district);
        if (!districtHasData) {
            const basePrices = {
                'Paddy': { max: 2300, min: 2000 },
                'Cotton': { max: 7500, min: 6800 },
                'Turmeric': { max: 13000, min: 11000 },
                'Chilli': { max: 19000, min: 15000 },
                'Maize': { max: 2200, min: 1800 },
                'Sugarcane': { max: 3400, min: 2900 },
                'Groundnut': { max: 6600, min: 5800 },
                'Black Gram': { max: 7900, min: 7000 },
                'Green Gram': { max: 8100, min: 7200 },
                'Bengal Gram': { max: 5400, min: 4800 },
                'Red Gram': { max: 7300, min: 6500 },
                'Jowar': { max: 3000, min: 2400 },
                'Bajra': { max: 2400, min: 1900 },
                'Ragi': { max: 3300, min: 2700 },
                'Soybean': { max: 4800, min: 4200 },
                'Sunflower': { max: 6100, min: 5300 },
                'Sesamum': { max: 13500, min: 11500 },
                'Castor Seed': { max: 6300, min: 5500 },
                'Mustard Seed': { max: 5800, min: 5000 },
                'Tobacco': { max: 18000, min: 14000 },
                'Tomato': { max: 2100, min: 1500 },
                'Onion': { max: 2500, min: 1900 },
                'Banana': { max: 1800, min: 1200 },
                'Mango': { max: 5000, min: 3500 },
                'Coconut': { max: 2200, min: 1500 },
                'Papaya': { max: 2000, min: 1400 },
                'Cashewnut': { max: 9500, min: 7500 },
                'Coffee': { max: 14000, min: 11000 },
                'Black Pepper': { max: 55000, min: 48000 }
            };
            const bp = basePrices[crop] || { max: 2000, min: 1800 };
            
            const seed = district.charCodeAt(0) + district.charCodeAt(district.length - 1);
            const priceSeed1 = (seed % 15) * 10;
            const priceSeed2 = (seed % 25) * 8;
            
            const generated = [
                {
                    mandi: `${district} Adarsha Market Yard`,
                    district: district,
                    maxPrice: bp.min + 100 + priceSeed1,
                    minPrice: bp.min - 50 + priceSeed1,
                    trend: parseFloat((1.2 - (seed % 3) * 0.8).toFixed(1))
                },
                {
                    mandi: `${district} Cooperative Mandi`,
                    district: district,
                    maxPrice: bp.min + 50 + priceSeed2,
                    minPrice: bp.min - 100 + priceSeed2,
                    trend: parseFloat((0.8 + (seed % 4) * 0.4).toFixed(1))
                }
            ];
            
            generated.forEach(item => {
                if (item.minPrice >= item.maxPrice) {
                    item.minPrice = item.maxPrice - 150;
                }
            });
            
            listData = [...listData, ...generated];
        }
    }

    const filteredData = district === 'all' 
        ? listData 
        : listData.filter(d => d.district === district);

    if (filteredData.length === 0) {
        ratesList.innerHTML = '<p style="text-align:center; padding: 20px; color: var(--text-muted); font-size: 13px;">No mandi rates found for selected filters.</p>';
        return;
    }

    filteredData.forEach(item => {
        const isUp = item.trend >= 0;
        const trendClass = isUp ? 'trend-up' : 'trend-down';
        const trendArrow = isUp ? '▲' : '▼';
        
        const row = document.createElement('div');
        row.className = 'list-item';
        row.innerHTML = `
            <div>
                <strong style="font-size:15px; color:var(--text-main);">${item.mandi}</strong>
                <p style="font-size:12px; color:var(--text-muted); margin-top:4px;">District: ${item.district}</p>
            </div>
            <div style="text-align:right;">
                <span class="price-tag">₹${item.maxPrice}</span>
                <span class="price-trend ${trendClass}">
                    ${trendArrow} ${Math.abs(item.trend)}%
                </span>
            </div>
        `;
        ratesList.appendChild(row);
    });
}

function renderTrendGraph(crop) {
    const chart = document.getElementById('mandi-trend-chart');
    chart.innerHTML = '';

    let history = WEEKLY_TRENDS[crop];
    if (!history) {
        const basePrices = {
            'Paddy': 2150,
            'Cotton': 7200,
            'Turmeric': 12500,
            'Chilli': 17500,
            'Maize': 2000,
            'Sugarcane': 3150,
            'Groundnut': 6200,
            'Black Gram': 7450,
            'Green Gram': 7650,
            'Bengal Gram': 5100,
            'Red Gram': 6900,
            'Jowar': 2700,
            'Bajra': 2150,
            'Ragi': 3000,
            'Soybean': 4500,
            'Sunflower': 5700,
            'Sesamum': 12500,
            'Castor Seed': 5900,
            'Mustard Seed': 5400,
            'Tobacco': 16000,
            'Tomato': 1800,
            'Onion': 2200,
            'Banana': 1500,
            'Mango': 4200,
            'Coconut': 1850,
            'Papaya': 1700,
            'Cashewnut': 8500,
            'Coffee': 12500,
            'Black Pepper': 51500
        };
        const bp = basePrices[crop] || 2000;
        const seed = crop.charCodeAt(0) + crop.charCodeAt(crop.length - 1);
        history = [];
        let current = bp - 80 + (seed % 10) * 16;
        for (let i = 0; i < 7; i++) {
            current += ((seed + i) % 7) * 15 - 45;
            history.push(Math.round(current));
        }
    }
    const maxVal = Math.max(...history);
    const minVal = Math.min(...history);
    
    // Label indices (simulating Wed - Tue past week)
    const days = ['Wed', 'Thu', 'Fri', 'Sat', 'Sun', 'Mon', 'Tue'];

    history.forEach((price, idx) => {
        // Calculate height percentage relative to maximum price (so it looks visually accurate)
        // Set minimum height of 20% so it's always clear
        const pctHeight = ((price) / maxVal) * 100;
        
        const barWrapper = document.createElement('div');
        barWrapper.className = 'mandi-chart-bar-wrapper';
        barWrapper.innerHTML = `
            <div class="mandi-chart-bar" style="height: ${pctHeight}%;" data-val="₹${price}"></div>
            <span class="mandi-chart-label">${days[idx]}</span>
        `;
        chart.appendChild(barWrapper);
    });
}


// --- AI CROP DOCTOR SCAN ENGINE ---
function selectScanSpecimen(type) {
    AppState.selectedSpecimen = type;
    
    const preview = document.getElementById('scanned-image-preview');
    const promptText = document.getElementById('camera-instructions');
    const startBtn = document.getElementById('start-scan-btn');

    // Display image previews according to choice
    preview.style.display = 'block';
    promptText.style.display = 'none';
    startBtn.disabled = false;

    if (type === 'blast') {
        preview.src = 'https://images.unsplash.com/photo-1530595467537-0b5996c41f2d?auto=format&fit=crop&w=400&q=80'; // Dry autumn paddy colors
    } else if (type === 'blight') {
        preview.src = 'https://images.unsplash.com/photo-1618331835717-801e976710b2?auto=format&fit=crop&w=400&q=80'; // Crumpled dry leaf
    } else if (type === 'healthy') {
        preview.src = 'https://images.unsplash.com/photo-1523348837708-15d4a09cfac2?auto=format&fit=crop&w=400&q=80'; // Lush green leaves
    }
}

function triggerSpecimenUpload() {
    document.getElementById('specimen-file-input').click();
}

function handleSpecimenFileUpload(input) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const preview = document.getElementById('scanned-image-preview');
            const promptText = document.getElementById('camera-instructions');
            const startBtn = document.getElementById('start-scan-btn');

            preview.src = e.target.result;
            preview.style.display = 'block';
            promptText.style.display = 'none';
            startBtn.disabled = false;

            AppState.selectedSpecimen = 'custom';
            showToast('Specimen uploaded successfully!');
        };
        reader.readAsDataURL(input.files[0]);
    }
}

function runCropDiagnostics() {
    const laser = document.getElementById('scan-laser-line');
    const startBtn = document.getElementById('start-scan-btn');
    const results = document.getElementById('diagnosis-results');

    // Show laser and disable button
    laser.style.display = 'block';
    startBtn.disabled = true;
    results.style.display = 'none';

    showToast('Analyzing crop tissue cells...');

    // 2.5 second simulated scan process
    setTimeout(() => {
        laser.style.display = 'none';
        startBtn.disabled = false;
        
        let report = null;

        // Custom uploads trigger a randomized but detailed diagnostic
        if (AppState.selectedSpecimen === 'custom') {
            const types = ['blast', 'blight', 'healthy'];
            const randType = types[Math.floor(Math.random() * types.length)];
            report = SPECIMENS[randType];
        } else {
            report = SPECIMENS[AppState.selectedSpecimen];
        }

        if (report) {
            // Render Report
            document.getElementById('result-severity').className = `badge ${report.severityClass}`;
            document.getElementById('result-severity').textContent = report.severity;
            document.getElementById('result-disease-name').textContent = report.disease;
            document.getElementById('result-confidence').textContent = report.confidence;
            document.getElementById('result-visual-emoticon').textContent = report.emoticon;
            document.getElementById('result-symptoms').textContent = report.symptoms;
            document.getElementById('result-organic').textContent = report.organic;
            document.getElementById('result-chemical').textContent = report.chemical;
            document.getElementById('result-doctor-tip').textContent = report.tip;

            results.style.display = 'block';
            showToast('Diagnostics completed!');
            
            // Scroll to report
            results.scrollIntoView({ behavior: 'smooth' });
        }
    }, 2500);
}


// --- GPS AND GEOLOCATION ENGINES ---
function calculateDistance(lat1, lon1, lat2, lon2) {
    const R = 6371; // Radius of Earth in km
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
              Math.sin(dLon/2) * Math.sin(dLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c;
}

function detectGPSLocation(isDashboardSync = false) {
    if (!navigator.geolocation) {
        showToast('Geolocation is not supported by your browser.', 'error');
        return;
    }

    showToast('📍 Requesting GPS coordinates...');

    navigator.geolocation.getCurrentPosition(
        (position) => {
            const userLat = position.coords.latitude;
            const userLon = position.coords.longitude;
            const accuracy = Math.round(position.coords.accuracy || 0);
            
            // Find nearest place in LOCATION_DATABASE
            let nearestLocation = null;
            let minDistance = Infinity;

            for (const [name, loc] of Object.entries(LOCATION_DATABASE)) {
                const dist = calculateDistance(userLat, userLon, loc.lat, loc.lon);
                if (dist < minDistance) {
                    minDistance = dist;
                    nearestLocation = name;
                }
            }

            if (nearestLocation) {
                showToast(`📍 Location Detected: ${nearestLocation} (${LOCATION_DATABASE[nearestLocation].state})`, 'success');
                
                if (isDashboardSync) {
                    if (AppState.user) {
                        AppState.user.region = nearestLocation;
                        AppState.user.mandal = MANDALS_DATABASE[nearestLocation] ? MANDALS_DATABASE[nearestLocation][0] : '';
                        sessionStorage.setItem('kisan_mitra_user', JSON.stringify(AppState.user));
                        localStorage.setItem(`km_reg_profile_${AppState.user.phone}`, JSON.stringify(AppState.user));
                    } else {
                        const dropdown = document.getElementById('reg-region');
                        if (dropdown) {
                            dropdown.value = nearestLocation;
                            dropdown.dispatchEvent(new Event('change'));
                        }
                    }
                    updateDashboardUI();
                    
                    const mapCard = document.getElementById('gps-map-card');
                    const mapIframe = document.getElementById('gps-map-iframe');
                    if (mapCard && mapIframe) {
                        mapIframe.src = `https://maps.google.com/maps?q=${userLat},${userLon}&t=&z=15&ie=UTF8&iwloc=&output=embed`;
                        mapCard.style.display = 'block';
                        document.getElementById('gps-coords-text').textContent = `${userLat.toFixed(5)}, ${userLon.toFixed(5)}`;
                        document.getElementById('gps-accuracy-text').textContent = `${accuracy}m`;
                    }
                } else {
                    const dropdown = document.getElementById('reg-region');
                    if (dropdown) {
                        dropdown.value = nearestLocation;
                        dropdown.dispatchEvent(new Event('change'));
                    }
                    
                    const regMapContainer = document.getElementById('reg-map-container');
                    const regMapIframe = document.getElementById('reg-map-iframe');
                    if (regMapContainer && regMapIframe) {
                        regMapIframe.src = `https://maps.google.com/maps?q=${userLat},${userLon}&t=&z=15&ie=UTF8&iwloc=&output=embed`;
                        regMapContainer.style.display = 'block';
                    }
                }
            } else {
                showToast('Could not map GPS coordinates to any database location.', 'error');
            }
        },
        (error) => {
            console.error('GPS Geolocation Error:', error);
            showToast('GPS access denied. Simulating Guntur region coords (16.30, 80.43)...', 'error');
            
            // Trigger simulated Guntur coordinates fallback for testing
            setTimeout(() => {
                const simulatedLat = 16.3067;
                const simulatedLon = 80.4365;
                const simulatedAccuracy = 15;
                const nearestLocation = 'Guntur';
                
                showToast(`📍 Location Detected: ${nearestLocation} (AP)`, 'success');
                
                if (isDashboardSync) {
                    if (AppState.user) {
                        AppState.user.region = nearestLocation;
                        AppState.user.mandal = MANDALS_DATABASE[nearestLocation] ? MANDALS_DATABASE[nearestLocation][0] : '';
                        sessionStorage.setItem('kisan_mitra_user', JSON.stringify(AppState.user));
                        localStorage.setItem(`km_reg_profile_${AppState.user.phone}`, JSON.stringify(AppState.user));
                    } else {
                        const dropdown = document.getElementById('reg-region');
                        if (dropdown) {
                            dropdown.value = nearestLocation;
                            dropdown.dispatchEvent(new Event('change'));
                        }
                    }
                    updateDashboardUI();
                    
                    const mapCard = document.getElementById('gps-map-card');
                    const mapIframe = document.getElementById('gps-map-iframe');
                    if (mapCard && mapIframe) {
                        mapIframe.src = `https://maps.google.com/maps?q=${simulatedLat},${simulatedLon}&t=&z=15&ie=UTF8&iwloc=&output=embed`;
                        mapCard.style.display = 'block';
                        document.getElementById('gps-coords-text').textContent = `${simulatedLat.toFixed(5)}, ${simulatedLon.toFixed(5)}`;
                        document.getElementById('gps-accuracy-text').textContent = `${simulatedAccuracy}m`;
                    }
                } else {
                    const dropdown = document.getElementById('reg-region');
                    if (dropdown) {
                        dropdown.value = nearestLocation;
                        dropdown.dispatchEvent(new Event('change'));
                    }
                    
                    const regMapContainer = document.getElementById('reg-map-container');
                    const regMapIframe = document.getElementById('reg-map-iframe');
                    if (regMapContainer && regMapIframe) {
                        regMapIframe.src = `https://maps.google.com/maps?q=${simulatedLat},${simulatedLon}&t=&z=15&ie=UTF8&iwloc=&output=embed`;
                        regMapContainer.style.display = 'block';
                    }
                }
            }, 1200);
        },
        { enableHighAccuracy: true, timeout: 5000 }
    );
}


function populateMandiDistrictsDropdown() {
    const dropdown = document.getElementById('mandi-filter-district');
    if (!dropdown) return;
    dropdown.innerHTML = '';
    
    // Add "All Markets" option
    const allOption = document.createElement('option');
    allOption.value = 'all';
    allOption.textContent = 'All Markets';
    dropdown.appendChild(allOption);
    
    // Sort locations alphabetically
    const keys = Object.keys(LOCATION_DATABASE).sort();
    keys.forEach(key => {
        const option = document.createElement('option');
        option.value = key;
        option.textContent = `${key} (${LOCATION_DATABASE[key].state === 'Telangana' ? 'TS' : 'AP'})`;
        dropdown.appendChild(option);
    });
}


// --- STARTUP LOADER ---
window.addEventListener('DOMContentLoaded', initApp);
