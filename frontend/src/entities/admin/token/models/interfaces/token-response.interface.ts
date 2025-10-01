import { TokenDto } from '@/entities/admin';

export interface ITokenResponse {
  access_token: TokenDto;
  refresh_token: TokenDto;
  token_type: TokenDto;
  expires_in: TokenDto;
}
