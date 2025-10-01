import {IToken, ITokenRefreshRequest} from '@/entities/admin';

export interface ITokenStore {
  logged: boolean;
  token: IToken | null;

  login: (username: string, password: string) => Promise<void>;
  refresh: (request: ITokenRefreshRequest) => Promise<void>;
  logout: () => void;
}
