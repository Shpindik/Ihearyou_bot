export const convertQuery = <T extends object>(data?: T): string => {
  if (!data) return '';

  const keys = (Object.keys(data) as Array<keyof T>).filter(
    (key) => !!data[key],
  );

  if (!keys.length) return '';

  return keys.reduce((previous, current, index) => {
    const query = Array.isArray(data[current])
      ? data[current].join(',')
      : data[current];

    if (!query) return '';

    let value = previous + `${current as string}=${query}`;

    if (index !== keys.length - 1) value += '&';

    return value;
  }, '?');
};
