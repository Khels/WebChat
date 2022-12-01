export function required(val: string) {
  return (val && val.length > 0 || 'Это поле обязательно');
}
