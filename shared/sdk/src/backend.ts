export enum BackendAction {
    LINK = 'link_account',
    UNLINK = 'unlink_account',
    DELETE = 'delete_account',
    RECLAIM = 'reclaim_account',
    GENERATE_QR = 'generate_qr',
    PROFILE = 'get_profile',
    HANDSHAKE = 'handshake',
}

export enum BackendEvent {
    ACCOUNT_LINKED = 'account_linked',
    ACCOUNT_UNLINKED = 'account_unlinked',
    ACCOUNT_DELETED = 'account_deleted',
    ACCOUNT_RECLAIMED = 'account_reclaimed',
    QR_GENERATED = 'qr_generated',
    PROFILE_OBTAINED = 'profile_obtained'
}

export enum BackendSuccessMessage {
    ACCOUNT_LINKED = 'Successfully linked! Please save your nexsplit UID somewhere for account recovery.\n\nUse \`/qrcode\` to obtain your unique nexsplit QR code.\n\nnexsplit UID: ',
    ACCOUNT_UNLINKED = 'Your nexsplit account has successfully unlinked: ',
    ACCOUNT_DELETED = 'Successfully deleted nexsplit account.',
    ACCOUNT_RECLAIMED = 'Successfully reclaimed nexsplit account. Welcome back!',
    QR_GENERATED = 'Successfully generated your nexsplit QR code!\n\nUse it as a profile picture in-game as you play nexsplit-hosted matches to ensure MMR points become valid.',
}

export interface BaseRequest {
    interaction_id: string;
    discord_id: string;
    guild_id?: string | null;
}

export interface ProfileRequest extends BaseRequest {
    action: BackendAction.PROFILE;
    discord_id: string;
}

export interface LinkRequest extends BaseRequest {
    action: BackendAction.LINK;
    standoff2_id: string;
    pin: string;
}

export interface UnlinkRequest extends BaseRequest {
    action: BackendAction.UNLINK;
    target: string;    
    pin: string;
}

export interface DeleteRequest extends BaseRequest {
    action: BackendAction.DELETE;
    pin: string;
}

export interface ReclaimRequest extends BaseRequest {
    action: BackendAction.RECLAIM;
    nexsplit_uid: string;    
    pin: string;
}

export interface GenerateQrRequest extends BaseRequest {
    action: BackendAction.GENERATE_QR;
}

export interface HandshakeRequest extends BaseRequest {
    action: BackendAction.HANDSHAKE;
    token: string;    
}

export interface ErrorResponse {
    error: true;
    message: string;
    interaction_id?: string;
}

export interface BaseSuccessResponse {
    error?: false;
    discord_id: string;
    interaction_id: string;
}

export interface ProfileResponse extends BaseSuccessResponse {
    event: BackendEvent.PROFILE_OBTAINED;
    local_mmr: number;
    global_mmr: number;
    standoff2_id?: string;
    played_servers: { guild_id: string, mmr: number }[];
}

export interface LinkResponse extends BaseSuccessResponse {
    event: BackendEvent.ACCOUNT_LINKED;
    nexsplit_uid?: string;
    standoff2_id?: string;
    is_local_login?: boolean;
    message: BackendSuccessMessage.ACCOUNT_LINKED;
}

export interface UnlinkResponse extends BaseSuccessResponse {
    event: BackendEvent.ACCOUNT_UNLINKED;
    target: string;
    message: BackendSuccessMessage.ACCOUNT_UNLINKED;
}

export interface ReclaimResponse extends BaseSuccessResponse {
    event: BackendEvent.ACCOUNT_RECLAIMED;
    message: BackendSuccessMessage.ACCOUNT_RECLAIMED;
}

export interface DeleteResponse extends BaseSuccessResponse {
    event: BackendEvent.ACCOUNT_DELETED;
    is_global?: boolean;
    message: BackendSuccessMessage.ACCOUNT_DELETED;
}

export interface GenerateQrResponse extends BaseSuccessResponse {
    event: BackendEvent.QR_GENERATED;
    message: BackendSuccessMessage.QR_GENERATED;
    qr_code_base64: string;
}

export type BackendRequest = ProfileRequest | LinkRequest | UnlinkRequest | DeleteRequest | ReclaimRequest | GenerateQrRequest | HandshakeRequest;
export type BackendSuccessResponse = ProfileResponse | LinkResponse | UnlinkResponse | DeleteResponse | ReclaimResponse | GenerateQrResponse;

export type BackendResponse = ErrorResponse | BackendSuccessResponse;

export class BackendError extends Error {
    constructor(message: string) {
        super(message);
        this.name = 'BackendError';
    }
}