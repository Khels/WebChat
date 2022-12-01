export interface TokenResponse {
  accessToken: string;
  refreshToken: string;
}

export interface User {
  id: number;
  username: string;
  firstName: string;
  lastName: string;
  lastOnline?: Date;
  isActive: boolean;
  isAdmin: boolean;
}
