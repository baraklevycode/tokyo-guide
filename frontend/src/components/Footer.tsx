export default function Footer() {
  return (
    <footer className="bg-gray-50 border-t border-gray-100 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-2">
            <span className="text-xl">⛩️</span>
            <span className="font-semibold text-gray-700">מדריך טוקיו</span>
          </div>

          <p className="text-sm text-gray-500 text-center md:text-right max-w-md">
            מבוסס על{" "}
            <a
              href="https://www.ptitim.com/tokyoguide/"
              target="_blank"
              rel="noopener noreferrer"
              className="text-pink-600 hover:text-pink-700 underline"
            >
              המדריך של פתיתים
            </a>{" "}
            &mdash; כל הזכויות שמורות לגל, פתיתים.
          </p>

          <div className="flex items-center gap-4 text-sm text-gray-500">
            <a
              href="https://www.google.com/maps/d/viewer?mid=1I0o12hoecmBorcEsinQqw4nhTDG7adU"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-gray-700 transition-colors"
            >
              המפה הסודית
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
