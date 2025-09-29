module.exports = {
  extends: [
    'stylelint-config-standard',
    'stylelint-config-recommended',
    'stylelint-config-tailwindcss',
  ],
  plugins: ['stylelint-order'],
  rules: {
    'at-rule-no-unknown': [
      true,
      {
        ignoreAtRules: [
          'tailwind',
          'apply',
          'variants',
          'responsive',
          'screen',
          'layer',
        ],
      },
    ],
    'order/properties-alphabetical-order': true,
  },
};
