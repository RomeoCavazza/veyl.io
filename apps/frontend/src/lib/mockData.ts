// Realistic mock data for Instagram Trends Intelligence Platform

export interface InstagramPost {
  id: string;
  username: string;
  fullName: string;
  avatar: string;
  caption: string;
  hashtags: string[];
  media_type: 'IMAGE' | 'VIDEO' | 'CAROUSEL_ALBUM';
  media_url: string;
  thumbnail_url?: string;
  permalink: string;
  timestamp: string;
  like_count: number;
  comments_count: number;
  engagement_rate: number;
  reach?: number;
  impressions?: number;
  saves?: number;
}

export interface HashtagData {
  name: string;
  post_count: number;
  recent_growth: number;
  avg_engagement: number;
  trending_score: number;
}

export interface AnalyticsMetric {
  label: string;
  value: number;
  change: number;
  trend: 'up' | 'down' | 'stable';
}

// Realistic Instagram creators/influencers
const mockCreators = [
  { username: 'selenagomez', fullName: 'Selena Gomez', followers: '428.6M' },
  { username: 'cristiano', fullName: 'Cristiano Ronaldo', followers: '615.2M' },
  { username: 'kyliejenner', fullName: 'Kylie Jenner', followers: '398.4M' },
  { username: 'leomessi', fullName: 'Leo Messi', followers: '502.1M' },
  { username: 'beyonce', fullName: 'Beyoncé', followers: '315.8M' },
  { username: 'arianagrande', fullName: 'Ariana Grande', followers: '378.2M' },
  { username: 'therock', fullName: 'Dwayne Johnson', followers: '396.5M' },
  { username: 'kimkardashian', fullName: 'Kim Kardashian', followers: '362.7M' },
  { username: 'nike', fullName: 'Nike', followers: '305.4M' },
  { username: 'natgeo', fullName: 'National Geographic', followers: '280.1M' },
];

// Realistic hashtags by category
export const trendingHashtags: HashtagData[] = [
  { name: 'fashion', post_count: 1247893, recent_growth: 34.2, avg_engagement: 4.8, trending_score: 92 },
  { name: 'makeup', post_count: 892456, recent_growth: 28.5, avg_engagement: 5.2, trending_score: 88 },
  { name: 'fitness', post_count: 1456789, recent_growth: 22.1, avg_engagement: 3.9, trending_score: 85 },
  { name: 'travel', post_count: 2134567, recent_growth: 18.7, avg_engagement: 4.5, trending_score: 82 },
  { name: 'food', post_count: 1678923, recent_growth: 25.3, avg_engagement: 4.1, trending_score: 80 },
  { name: 'art', post_count: 987654, recent_growth: 31.8, avg_engagement: 5.6, trending_score: 87 },
  { name: 'photography', post_count: 1523789, recent_growth: 15.2, avg_engagement: 3.7, trending_score: 76 },
  { name: 'nature', post_count: 1289456, recent_growth: 19.4, avg_engagement: 4.3, trending_score: 79 },
  { name: 'lifestyle', post_count: 2456789, recent_growth: 12.8, avg_engagement: 3.5, trending_score: 74 },
  { name: 'beauty', post_count: 1834567, recent_growth: 27.6, avg_engagement: 4.9, trending_score: 86 },
];

// Generate realistic posts
export const generateMockPosts = (hashtag: string = 'fashion', count: number = 50): InstagramPost[] => {
  const captions = [
    "Excited to share my new project! 🎬✨ #behindthescenes",
    "Summer vibes are finally here! 🌊☀️ Can't wait for more adventures",
    "Throwback to this amazing moment 💫 #memories",
    "New collection dropping soon... stay tuned! 🔥",
    "Grateful for all the love and support ❤️ #thankyou",
    "Living my best life right now 🌟 #blessed",
    "Behind the scenes of today's shoot 📸 #workinprogress",
    "Can't believe this view is real 😍 #wanderlust",
    "Monday motivation! Let's crush this week 💪 #mondaymood",
    "Simple moments make the best memories 🌸 #grateful",
  ];

  return Array.from({ length: count }, (_, i) => {
    const creator = mockCreators[i % mockCreators.length];
    const likes = Math.floor(Math.random() * 5000000) + 50000;
    const comments = Math.floor(likes * (Math.random() * 0.05 + 0.01));
    const reach = Math.floor(likes * (Math.random() * 3 + 2));
    const engagement_rate = Number(((likes + comments) / reach * 100).toFixed(2));
    
    return {
      id: `post_${Date.now()}_${i}`,
      username: creator.username,
      fullName: creator.fullName,
      avatar: `https://api.dicebear.com/7.x/avataaars/svg?seed=${creator.username}`,
      caption: captions[i % captions.length],
      hashtags: [hashtag, 'instagram', 'instagood', 'photooftheday'],
      media_type: ['IMAGE', 'VIDEO', 'CAROUSEL_ALBUM'][Math.floor(Math.random() * 3)] as any,
      media_url: `https://picsum.photos/800/800?random=${i}`,
      thumbnail_url: `https://picsum.photos/400/400?random=${i}`,
      permalink: `https://instagram.com/p/${Math.random().toString(36).substr(2, 11)}`,
      timestamp: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString(),
      like_count: likes,
      comments_count: comments,
      engagement_rate,
      reach,
      impressions: Math.floor(reach * 1.2),
      saves: Math.floor(likes * 0.15),
    };
  });
};

// Dashboard KPIs
export const dashboardMetrics: AnalyticsMetric[] = [
  { label: 'Total Searches', value: 2847, change: 34.2, trend: 'up' },
  { label: 'Posts Analyzed', value: 45892, change: 28.5, trend: 'up' },
  { label: 'Hashtags Tracked', value: 156, change: 12.1, trend: 'up' },
  { label: 'Active Clients', value: 23, change: 8.3, trend: 'up' },
];

// Chart data for analytics
export const engagementTrendData = [
  { date: '2025-01-15', engagement: 3.2, reach: 125000, impressions: 150000 },
  { date: '2025-01-16', engagement: 3.8, reach: 142000, impressions: 168000 },
  { date: '2025-01-17', engagement: 4.1, reach: 156000, impressions: 182000 },
  { date: '2025-01-18', engagement: 3.9, reach: 148000, impressions: 175000 },
  { date: '2025-01-19', engagement: 4.5, reach: 178000, impressions: 210000 },
  { date: '2025-01-20', engagement: 4.8, reach: 192000, impressions: 228000 },
  { date: '2025-01-21', engagement: 4.2, reach: 165000, impressions: 195000 },
];

export const topPerformingCreators = [
  { username: 'selenagomez', posts: 145, avg_engagement: 5.2, total_reach: 12500000 },
  { username: 'cristiano', posts: 98, avg_engagement: 4.8, total_reach: 15200000 },
  { username: 'kyliejenner', posts: 167, avg_engagement: 5.6, total_reach: 11800000 },
  { username: 'arianagrande', posts: 134, avg_engagement: 4.9, total_reach: 10200000 },
  { username: 'therock', posts: 89, avg_engagement: 4.5, total_reach: 9500000 },
];

// Connected Pages (for Profile)
export interface ConnectedPage {
  id: string;
  name: string;
  username: string;
  category: string;
  followers: string;
  verified: boolean;
  profile_picture: string;
}

export const connectedPages: ConnectedPage[] = [
  {
    id: 'page_1',
    name: 'Insider Trends Official',
    username: '@insidertrends',
    category: 'Analytics & Data',
    followers: '45.2K',
    verified: true,
    profile_picture: 'https://api.dicebear.com/7.x/shapes/svg?seed=insidertrends',
  },
  {
    id: 'page_2',
    name: 'Fashion Insights Hub',
    username: '@fashioninsights',
    category: 'Fashion & Beauty',
    followers: '128.5K',
    verified: true,
    profile_picture: 'https://api.dicebear.com/7.x/shapes/svg?seed=fashioninsights',
  },
  {
    id: 'page_3',
    name: 'Trend Analytics Pro',
    username: '@trendanalytics',
    category: 'Business Tools',
    followers: '67.8K',
    verified: false,
    profile_picture: 'https://api.dicebear.com/7.x/shapes/svg?seed=trendanalytics',
  },
];
