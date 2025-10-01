import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      screens: {
        fine: { raw: '(hover: hover) and (pointer: fine)' },
        '3xl': '1920px',
      },
      colors: {
        ui: {
          green: {
            primary: '#ddff95',
          },
          purple: {
            primary: '#8028aa',
            secondary: '#f6f2ff',
            disabled: '#c192d3',
          },
          gray: {
            disabled: '#dadada',
          },
          text: {
            disabled: '#A7A7A7',
          },
          red: {
            error: '#FF003B',
          },
        },
      },
      boxShadow: {
        ui: '0px 2px 16px 0px rgba(0, 0, 0, 0.24)',
      },
      fontWeight: {
        ui: '550',
      },
      fontSize: {
        '1xl': '22px',
        '2xxl': '28px',
        '3xxl': '32px',
        '4xl': '44px',
      },
      fontFamily: {
        sans: ['Nekst', 'sans-serif'],
      },
      keyframes: {
        'slide-up': {
          '0%': { transform: 'translateY(100%)' },
          '100%': { transform: 'translateY(0)' },
        },
        'slide-down': {
          '0%': { transform: 'translateY(0)' },
          '100%': { transform: 'translateY(100%)' },
        },
        zoomIn: {
          '0%': { transform: 'scale(1)' },
          '50%': { transform: 'scale(1.5)' },
          '100%': { transform: 'scale(1)' },
        },
        zoomOut: {
          '0%': { transform: 'scale(1)' },
          '50%': { transform: 'scale(1.5)' },
          '100%': { transform: 'scale(1)' },
        },

        'opacity-expand': {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        'opacity-collapse': {
          '0%': { opacity: '1' },
          '100%': { opacity: '0' },
        },
        'bubble-expand': {
          '0%': { transform: 'scale(0)' },
          '100%': { transform: 'scale(1)' },
        },
        'bubble-collapse': {
          '0%': { transform: 'scale(1)' },
          '100%': { transform: 'scale(0)' },
        },
        'width-expand': {
          '0%': { width: '0px', overflow: 'hidden' },
          '100%': { width: '*', overflow: 'hidden' },
        },
        'width-collapse': {
          '0%': { width: '*', overflow: 'hidden' },
          '100%': { width: '0px', overflow: 'hidden' },
        },
        'height-expand': {
          '0%': { maxHeight: '0px', overflow: 'hidden' },
          '100%': { maxHeight: '1000px' },
        },
        'height-collapse': {
          '0%': { maxHeight: '1000px' },
          '100%': { maxHeight: '0px', overflow: 'hidden' },
        },
        'height-expand-fixed': {
          '0%': { height: '0px', overflow: 'hidden' },
          '100%': { height: '*' },
        },
        'height-collapse-fixed': {
          '0%': { height: '*' },
          '100%': { height: '0px', overflow: 'hidden' },
        },
        'dropdown-expand': {
          '0%': {
            opacity: '0',
            height: '88%',
            transform: 'translateY(-10px) scaleY(0.92)',
          },
          '100%': {
            opacity: '1',
            height: 'auto',
            transform: 'translateY(0) scaleY(1)',
          },
        },
        'dropdown-collapse': {
          '0%': {
            opacity: '1',
            height: 'auto',
            transform: 'translateY(0) scaleY(1)',
          },
          '100%': {
            opacity: '0',
            height: '88%',
            transform: 'translateY(-10px) scaleY(0.92)',
          },
        },
        'dropdown-expand-reverse': {
          '0%': {
            opacity: '0',
            height: '88%',
            transform: 'translateY(10px) scaleY(0.92)',
          },
          '100%': {
            opacity: '1',
            height: 'auto',
            transform: 'translateY(0) scaleY(1)',
          },
        },
        'dropdown-collapse-reverse': {
          '0%': {
            opacity: '1',
            height: 'auto',
            transform: 'translateY(0) scaleY(1)',
          },
          '100%': {
            opacity: '0',
            height: '88%',
            transform: 'translateY(-10px) scaleY(0.92)',
          },
        },
        notificationIn: {
          '0%': { transform: 'translateY(100%)' },
          '100%': { transform: 'translateY(0)' },
        },
        notificationOut: {
          '0%': { transform: 'translateY(0)' },
          '100%': { transform: 'translateY(100%)' },
        },
        'loader-spin': {
          '0%': { transform: 'rotate(0deg) scale(1)' },
          '50%': { transform: 'rotate(180deg) scale(0.92)' },
          '100%': { transform: 'rotate(360deg) scale(1)' },
        },
        rotate: {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' },
        },
        rotateOut: {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(-360deg)' },
        },
        'spin-slow': {
          '0%': { transform: 'rotate(0deg)' },
          '20%': { transform: 'rotate(0deg)' },
          '25%': { transform: 'rotate(90deg)' },
          '45%': { transform: 'rotate(90deg)' },
          '50%': { transform: 'rotate(180deg)' },
          '70%': { transform: 'rotate(180deg)' },
          '75%': { transform: 'rotate(270deg)' },
          '95%': { transform: 'rotate(270deg)' },
          '100%': { transform: 'rotate(360deg)' },
        },
      },
      animation: {
        'slide-up': 'slide-up 0.2s ease forwards',
        'slide-down': 'slide-down 0.2s ease forwards',
        'opacity-expand': 'opacity-expand 150ms ease-in-out forwards',
        'opacity-collapse': 'opacity-collapse 150ms ease-in-out forwards',
        'bubble-expand': 'bubble-expand 150ms ease-in-out forwards',
        'bubble-collapse': 'bubble-collapse 150ms ease-in-out forwards',
        'width-expand': 'width-expand 150ms ease-in-out forwards',
        'width-collapse': 'width-collapse 150ms ease-in-out forwards',
        'height-expand': 'height-expand 150ms ease-in-out forwards',
        'height-collapse': 'height-collapse 150ms ease-in-out forwards',
        'height-expand-fixed': 'height-expand-fixed 150ms ease-in-out forwards',
        'height-collapse-fixed':
          'height-collapse-fixed 150ms ease-in-out forwards',
        'dropdown-expand':
          'dropdown-expand 150ms cubic-bezier(0.645, 0.045, 0.355, 1) forwards',
        'dropdown-collapse':
          'dropdown-collapse 150ms cubic-bezier(0.645, 0.045, 0.355, 1) forwards',
        'dropdown-expand-reverse':
          'dropdown-expand-reverse 150ms cubic-bezier(0.645, 0.045, 0.355, 1) forwards',
        'dropdown-collapse-reverse':
          'dropdown-collapse-reverse 150ms cubic-bezier(0.645, 0.045, 0.355, 1) forwards',
        zoomIn: 'zoomIn 0.3s ease-in-out',
        zoomOut: 'zoomOut 0.3s ease-in-out',
        notificationIn: 'notificationIn 0.3s ease-out forwards',
        notificationOut: 'notificationOut 0.3s ease-out forwards',
        'loader-spin': 'loader-spin 0.8s infinite linear',
        rotate: 'rotate 1s linear infinite',
        rotateOut: 'rotateOut 0.3s ease forwards',
        'spin-slow': 'spin-slow 4s infinite linear',
      },
    },
  },
  plugins: [],
};

export default config;
