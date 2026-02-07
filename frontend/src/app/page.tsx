import Link from "next/link";
import Header from "@/components/Header";
import Footer from "@/components/Footer";

const CATEGORIES = [
  { id: "neighborhoods", label: "שכונות ואזורים", icon: "🏘️", desc: "שינג׳וקו, שיבויה, הראג׳וקו, אסקוסה ועוד" },
  { id: "attractions", label: "אטרקציות וציוני דרך", icon: "⛩️", desc: "מקדשים, מוזיאונים, פארקים ותצפיות" },
  { id: "restaurants", label: "מסעדות ואוכל", icon: "🍜", desc: "ראמן, סושי, יקיטורי, קארי ורשימת הזהב" },
  { id: "hotels", label: "מלונות ולינה", icon: "🏨", desc: "איפה כדאי לישון ואיך לבחור מלון" },
  { id: "transportation", label: "תחבורה", icon: "🚃", desc: "מטרו, רכבות, IC card וניווט בעיר" },
  { id: "shopping", label: "קניות", icon: "🛍️", desc: "חנויות, שווקים, מזכרות ומה כדאי להביא" },
  { id: "cultural_experiences", label: "חוויות תרבותיות", icon: "🎎", desc: "טקסי תה, אונסן, קימונו ומסורות" },
  { id: "day_trips", label: "טיולי יום", icon: "🗻", desc: "קיוטו ויעדים נוספים מחוץ לטוקיו" },
  { id: "practical_tips", label: "טיפים שימושיים", icon: "💡", desc: "אינטרנט, כסף, שפה, שירותים ועוד" },
];

export default function HomePage() {
  return (
    <>
      <Header />

      <main className="flex-1">
        {/* Hero Section */}
        <section className="relative bg-gradient-to-bl from-pink-50 via-white to-rose-50 overflow-hidden">
          <div className="absolute inset-0 opacity-5">
            <div className="absolute top-10 left-10 text-9xl">⛩️</div>
            <div className="absolute bottom-10 right-10 text-9xl">🗼</div>
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-9xl">🌸</div>
          </div>

          <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 md:py-32">
            <div className="text-center max-w-3xl mx-auto">
              <h1 className="text-4xl md:text-6xl font-extrabold text-gray-900 leading-tight">
                איך לאכול את
                <span className="text-transparent bg-clip-text bg-gradient-to-l from-pink-600 to-rose-500">
                  {" "}טוקיו{" "}
                </span>
                כמו מקומי
              </h1>
              <p className="mt-6 text-lg md:text-xl text-gray-600 leading-relaxed">
                המדריך האישי והמקיף ביותר לטיול בטוקיו בעברית.
                מאות מסעדות, שכונות מעניינות, אטרקציות ייחודיות וטיפים שלא תמצאו במדריכים רגילים.
              </p>
              <div className="mt-8 flex flex-col sm:flex-row gap-4 justify-center">
                <Link
                  href="/sections"
                  className="inline-flex items-center justify-center px-8 py-3 rounded-xl bg-pink-600 text-white font-semibold hover:bg-pink-700 transition-colors shadow-lg shadow-pink-200"
                >
                  גלה את המדריך
                </Link>
                <Link
                  href="/sections/restaurants"
                  className="inline-flex items-center justify-center px-8 py-3 rounded-xl bg-white text-gray-700 font-semibold border border-gray-200 hover:border-pink-300 hover:text-pink-700 transition-colors"
                >
                  🍜 רשימת הזהב
                </Link>
              </div>
            </div>
          </div>
        </section>

        {/* Categories Grid */}
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <h2 className="text-2xl md:text-3xl font-bold text-gray-900 mb-8 text-center">
            מה מעניין אתכם?
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {CATEGORIES.map((cat) => (
              <Link
                key={cat.id}
                href={`/sections/${cat.id}`}
                className="group bg-white rounded-2xl border border-gray-100 p-6 hover:shadow-lg hover:border-pink-200 transition-all duration-300"
              >
                <div className="flex items-start gap-4">
                  <span className="text-3xl group-hover:scale-110 transition-transform duration-300">
                    {cat.icon}
                  </span>
                  <div>
                    <h3 className="text-lg font-bold text-gray-900 group-hover:text-pink-700 transition-colors">
                      {cat.label}
                    </h3>
                    <p className="text-sm text-gray-500 mt-1">{cat.desc}</p>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </section>

        {/* Chat CTA */}
        <section className="bg-gradient-to-l from-indigo-900 to-gray-900 text-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 text-center">
            <h2 className="text-2xl md:text-3xl font-bold mb-4">
              יש שאלה על טוקיו? שאלו אותי!
            </h2>
            <p className="text-gray-300 text-lg mb-8 max-w-2xl mx-auto">
              הצ&apos;אט החכם שלנו מבוסס על כל המידע שבמדריך ויכול לענות על כל שאלה
              בעברית - מסעדות, מלונות, תחבורה, קניות ועוד.
            </p>
            <p className="text-gray-400">
              לחצו על כפתור הצ&apos;אט בפינה השמאלית התחתונה כדי להתחיל
            </p>
          </div>
        </section>

        {/* Source Credit */}
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 text-center">
          <p className="text-gray-500">
            המדריך מבוסס על{" "}
            <a
              href="https://www.ptitim.com/tokyoguide/"
              target="_blank"
              rel="noopener noreferrer"
              className="text-pink-600 hover:text-pink-700 underline font-medium"
            >
              &quot;איך לאכול את טוקיו כמו מקומי&quot;
            </a>{" "}
            מאת גל, בלוג פתיתים.
          </p>
        </section>
      </main>

      <Footer />
    </>
  );
}
