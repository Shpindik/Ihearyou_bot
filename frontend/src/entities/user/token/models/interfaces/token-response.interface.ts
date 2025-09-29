import { TokenDto } from '@/entities/user/token/models/dtos/token.dto.ts';

export interface ITokenResponse {
  access_token: TokenDto;
  refresh_token: TokenDto;
  token_type: TokenDto;
  expires_in: TokenDto;
}
