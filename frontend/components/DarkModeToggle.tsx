'use client';

import { useEffect, useState } from 'react';
import Image from 'next/image';
import sunIcon from '../public/icon-sun.svg';
import moonIcon from '../public/icon-moon.svg';

export default function DarkModeToggle() {
  const [theme, setTheme] = useState<'light' | 'dark'>('light');

  useEffect(() => {
    const savedTheme = localStorage.getItem('theme') as 'light' | 'dark' | null;
    if (savedTheme) {
      setTheme(savedTheme);
      document.documentElement.classList.toggle('dark', savedTheme === 'dark');
    }
  }, []);

  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    localStorage.setItem('theme', newTheme);
    document.documentElement.classList.toggle('dark', newTheme === 'dark');
  };

  return (
    <button
      onClick={toggleTheme}
      className="relative flex items-center w-16 h-8 rounded-full bg-gray-300 dark:bg-gray-700 p-1 transition-all"
    >
      <div
        className={`absolute top-1 left-1 w-6 h-6 rounded-full bg-white shadow-md transform transition-transform ${
          theme === 'dark' ? 'translate-x-8' : ''
        }`}
      />
      <div className="flex justify-between w-full z-10 px-2">
        <Image src={sunIcon} alt="Light mode" width={20} height={20} />
        <Image src={moonIcon} alt="Dark mode" width={20} height={20} />
      </div>
    </button>
  );
}
