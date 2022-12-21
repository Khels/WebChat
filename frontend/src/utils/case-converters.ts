const TO_CAMEL_CASE = /([_][a-z])/ig;


function isArray(value: any): boolean {
  return Array.isArray(value);
}


function isObject(value: any): boolean {
  return value === Object(value)
      && !isArray(value)
      && typeof value !== 'function';
}


function toCamel(item: string): string {
  return item.replace(TO_CAMEL_CASE, (replacer: string) => {
      return replacer.toUpperCase()
          .replace('_', '');
  });
}


export function camelCaseKeys(value: any): any {
  if (isObject(value)) {
      const newObject = {};
      Object.keys(value)
        .forEach((key) => {
          newObject[toCamel(key)] = camelCaseKeys(value[key]);
        });
      return newObject;
  } else if (isArray(value)) {
      return value.map((item) => {
          return camelCaseKeys(item);
      });
  }
  return value;
}
