// types/project.ts
// Types partagés pour les projets et leurs données

export interface ProjectPost {
  id: string;
  author?: string;
  username?: string;
  caption?: string;
  media_url?: string;
  permalink?: string;
  posted_at?: string;
  fetched_at?: string;
  platform?: string;
  like_count?: number;
  comment_count?: number;
  share_count?: number;
  view_count?: number;
  score_trend?: number;
  hashtags?: string[];
  mentions?: string[];
  location?: string;
  media_type?: string;
  thumbnail_url?: string;
  external_id?: string;
}

export interface CreatorLink {
  id: number;
  creator_username: string;
  platform_id?: number;
  platform?: string;
  added_at?: string;
}

export interface HashtagLink {
  id: number;
  link_id?: number;
  name: string;
  platform_id?: number;
  platform?: string;
  added_at?: string;
  posts?: number;
  growth?: string;
  engagement?: number;
}

export interface CreatorCard {
  handle: string;
  platform: string;
  profile_picture: string;
  linkId?: number;
}

export interface HashtagEntry {
  id: number;
  linkId: number;
  name: string;
  posts: number;
  growth: string;
  engagement: number;
  platform: string;
}

export interface ProjectData {
  id: string;
  user_id: string;
  name: string;
  description?: string;
  status: string;
  platforms: string[];
  scope_type?: string;
  scope_query?: string;
  creators_count?: number;
  posts_count?: number;
  signals_count?: number;
  last_run_at?: string;
  last_signal_at?: string;
  created_at: string;
  updated_at: string;
  hashtags?: HashtagLink[];
  creators?: CreatorLink[];
}


