"use client";

import { useState, useEffect } from "react";
import { useTranslations } from 'next-intl';
import { Link } from '@/i18n/routing';
import LanguageSwitcher from "../../app/components/LanguageSwitcher/LanguageSwitcher";

export default function Navbar() {
  const t = useTranslations('navbar');
  const [scrolled, setScrolled] = useState(false);
  const [themeDark, setThemeDark] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const theme = entry.target.getAttribute("data-theme");
            setThemeDark(theme === "dark");
          }
        });
      },
      { threshold: 0.3 }
    );
    document.querySelectorAll("[data-theme]").forEach((el) => observer.observe(el));
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    document.body.classList.toggle("theme-dark", themeDark);
    return () => document.body.classList.remove("theme-dark");
  }, [themeDark]);

  return (
    <nav
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-700 ${
        scrolled ? "backdrop-blur-xl py-4" : "bg-transparent py-6"
      }`}
    >
      <div className="max-w-[1400px] mx-auto px-8 flex items-center justify-between">
        <div className="flex items-center gap-12">
          <div className="flex items-center gap-2">
            <div
              className={`w-5 h-5 rounded-full transition-colors duration-700 ${
                scrolled || themeDark ? "bg-white" : "bg-black"
              }`}
            />
            <span className="text-xl tracking-tight transition-colors duration-700 text-inherit">
              MeshAi
            </span>
          </div>
          <div className="hidden lg:flex items-center gap-8 text-[13px] opacity-70">
            <a href="#" className="hover:opacity-100 transition-all">
              {t('products')}
            </a>
            <a href="#" className="hover:opacity-100 transition-all">
              {t('solutions')}
            </a>
            <a href="#" className="hover:opacity-100 transition-all">
              {t('pricing')}
            </a>
          </div>
        </div>

        <div className="flex items-center gap-6 text-[13px]">
          <LanguageSwitcher />
          <Link href="/dashboard" className="opacity-70 hover:opacity-100">{t('login')}</Link>
          <Link
            href="/dashboard"
            className={`px-6 py-2.5 rounded-full transition-all duration-700 ${
              themeDark
                ? "bg-white text-black hover:bg-slate-200"
                : "bg-black text-white hover:bg-slate-800"
            }`}
          >
            {t('getStarted')}
          </Link>
        </div>
      </div>
    </nav>
  );
}
