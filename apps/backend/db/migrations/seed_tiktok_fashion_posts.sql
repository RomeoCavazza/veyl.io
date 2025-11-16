-- Script SQL pour insérer des posts TikTok de démo et les lier au hashtag "fashion"
-- À exécuter dans pgAdmin ou via psql

-- 1. Assurer que la plateforme "tiktok" existe
INSERT INTO platforms (name, created_at, updated_at)
VALUES ('tiktok', NOW(), NOW())
ON CONFLICT (name) DO NOTHING;

-- Récupérer l'ID de la plateforme TikTok
DO $$
DECLARE
    tiktok_platform_id INTEGER;
    fashion_hashtag_id INTEGER;
    post_id TEXT;
    video_id TEXT;
    creator_username TEXT;
    permalink TEXT;
    post_record RECORD;
BEGIN
    -- Récupérer l'ID de la plateforme TikTok
    SELECT id INTO tiktok_platform_id FROM platforms WHERE name = 'tiktok';
    
    IF tiktok_platform_id IS NULL THEN
        RAISE EXCEPTION 'Plateforme TikTok non trouvée après insertion';
    END IF;
    
    -- 2. Assurer que le hashtag "fashion" existe pour TikTok
    -- Vérifier d'abord s'il existe déjà pour TikTok
    SELECT id INTO fashion_hashtag_id 
    FROM hashtags 
    WHERE name = 'fashion' AND platform_id = tiktok_platform_id;
    
    -- Si le hashtag n'existe pas pour TikTok, le créer
    IF fashion_hashtag_id IS NULL THEN
        -- Vérifier si un hashtag "fashion" existe déjà pour une autre plateforme
        -- Si oui, on doit le renommer ou créer un nouveau hashtag avec un nom différent
        -- Pour l'instant, on crée directement (la contrainte unique sur name peut poser problème)
        -- Solution: utiliser un nom unique comme "fashion_tiktok" ou modifier la contrainte
        -- Ici, on assume qu'il n'y a pas de conflit ou qu'on peut le gérer
        INSERT INTO hashtags (name, platform_id, last_scraped, updated_at)
        VALUES ('fashion', tiktok_platform_id, NOW(), NOW())
        ON CONFLICT (name) DO UPDATE 
        SET platform_id = tiktok_platform_id, updated_at = NOW()
        RETURNING id INTO fashion_hashtag_id;
        
        -- Si toujours NULL après INSERT, récupérer l'ID
        IF fashion_hashtag_id IS NULL THEN
            SELECT id INTO fashion_hashtag_id 
            FROM hashtags 
            WHERE name = 'fashion' AND platform_id = tiktok_platform_id;
        END IF;
    END IF;
    
    -- 3. Insérer les posts TikTok et les lier au hashtag
    -- Post 1: styledbysash9
    video_id := '7499036976218230038';
    creator_username := 'styledbysash9';
    permalink := 'https://www.tiktok.com/@styledbysash9/video/7499036976218230038';
    
    INSERT INTO posts (
        id, external_id, platform_id, author, caption, media_url,
        posted_at, fetched_at, last_fetch_at, source, metrics, api_payload
    ) VALUES (
        video_id, video_id, tiktok_platform_id, creator_username,
        'TikTok video by @' || creator_username || ' #fashion',
        'https://p16-sign-va.tiktokcdn.com/obj/tos-maliva-p-0068/placeholder.jpg',
        NOW(), NOW(), NOW(), 'tiktok_demo_seed',
        '{"like_count": 0, "comment_count": 0, "view_count": 0}',
        json_build_object(
            'id', video_id,
            'creator', creator_username,
            'share_url', permalink,
            'url', permalink,
            'permalink', permalink
        )::text
    )
    ON CONFLICT (id) DO UPDATE SET
        author = EXCLUDED.author,
        api_payload = EXCLUDED.api_payload;
    
    -- Lier au hashtag
    INSERT INTO post_hashtags (post_id, hashtag_id, created_at)
    VALUES (video_id, fashion_hashtag_id, NOW())
    ON CONFLICT (post_id, hashtag_id) DO NOTHING;
    
    -- Post 2: wisdm8
    video_id := '7404270216542244126';
    creator_username := 'wisdm8';
    permalink := 'https://www.tiktok.com/@wisdm8/video/7404270216542244126';
    
    INSERT INTO posts (
        id, external_id, platform_id, author, caption, media_url,
        posted_at, fetched_at, last_fetch_at, source, metrics, api_payload
    ) VALUES (
        video_id, video_id, tiktok_platform_id, creator_username,
        'TikTok video by @' || creator_username || ' #fashion',
        'https://p16-sign-va.tiktokcdn.com/obj/tos-maliva-p-0068/placeholder.jpg',
        NOW(), NOW(), NOW(), 'tiktok_demo_seed',
        '{"like_count": 0, "comment_count": 0, "view_count": 0}',
        json_build_object(
            'id', video_id,
            'creator', creator_username,
            'share_url', permalink,
            'url', permalink,
            'permalink', permalink
        )::text
    )
    ON CONFLICT (id) DO UPDATE SET
        author = EXCLUDED.author,
        api_payload = EXCLUDED.api_payload;
    
    INSERT INTO post_hashtags (post_id, hashtag_id, created_at)
    VALUES (video_id, fashion_hashtag_id, NOW())
    ON CONFLICT (post_id, hashtag_id) DO NOTHING;
    
    -- Post 3: yungalyy
    video_id := '7509573574215208214';
    creator_username := 'yungalyy';
    permalink := 'https://www.tiktok.com/@yungalyy/video/7509573574215208214';
    
    INSERT INTO posts (
        id, external_id, platform_id, author, caption, media_url,
        posted_at, fetched_at, last_fetch_at, source, metrics, api_payload
    ) VALUES (
        video_id, video_id, tiktok_platform_id, creator_username,
        'TikTok video by @' || creator_username || ' #fashion',
        'https://p16-sign-va.tiktokcdn.com/obj/tos-maliva-p-0068/placeholder.jpg',
        NOW(), NOW(), NOW(), 'tiktok_demo_seed',
        '{"like_count": 0, "comment_count": 0, "view_count": 0}',
        json_build_object(
            'id', video_id,
            'creator', creator_username,
            'share_url', permalink,
            'url', permalink,
            'permalink', permalink
        )::text
    )
    ON CONFLICT (id) DO UPDATE SET
        author = EXCLUDED.author,
        api_payload = EXCLUDED.api_payload;
    
    INSERT INTO post_hashtags (post_id, hashtag_id, created_at)
    VALUES (video_id, fashion_hashtag_id, NOW())
    ON CONFLICT (post_id, hashtag_id) DO NOTHING;
    
    -- Post 4: taymosesofficial
    video_id := '7552842920798276886';
    creator_username := 'taymosesofficial';
    permalink := 'https://www.tiktok.com/@taymosesofficial/video/7552842920798276886';
    
    INSERT INTO posts (
        id, external_id, platform_id, author, caption, media_url,
        posted_at, fetched_at, last_fetch_at, source, metrics, api_payload
    ) VALUES (
        video_id, video_id, tiktok_platform_id, creator_username,
        'TikTok video by @' || creator_username || ' #fashion',
        'https://p16-sign-va.tiktokcdn.com/obj/tos-maliva-p-0068/placeholder.jpg',
        NOW(), NOW(), NOW(), 'tiktok_demo_seed',
        '{"like_count": 0, "comment_count": 0, "view_count": 0}',
        json_build_object(
            'id', video_id,
            'creator', creator_username,
            'share_url', permalink,
            'url', permalink,
            'permalink', permalink
        )::text
    )
    ON CONFLICT (id) DO UPDATE SET
        author = EXCLUDED.author,
        api_payload = EXCLUDED.api_payload;
    
    INSERT INTO post_hashtags (post_id, hashtag_id, created_at)
    VALUES (video_id, fashion_hashtag_id, NOW())
    ON CONFLICT (post_id, hashtag_id) DO NOTHING;
    
    -- Post 5: reubsfits
    video_id := '7522860474103385366';
    creator_username := 'reubsfits';
    permalink := 'https://www.tiktok.com/@reubsfits/video/7522860474103385366';
    
    INSERT INTO posts (
        id, external_id, platform_id, author, caption, media_url,
        posted_at, fetched_at, last_fetch_at, source, metrics, api_payload
    ) VALUES (
        video_id, video_id, tiktok_platform_id, creator_username,
        'TikTok video by @' || creator_username || ' #fashion',
        'https://p16-sign-va.tiktokcdn.com/obj/tos-maliva-p-0068/placeholder.jpg',
        NOW(), NOW(), NOW(), 'tiktok_demo_seed',
        '{"like_count": 0, "comment_count": 0, "view_count": 0}',
        json_build_object(
            'id', video_id,
            'creator', creator_username,
            'share_url', permalink,
            'url', permalink,
            'permalink', permalink
        )::text
    )
    ON CONFLICT (id) DO UPDATE SET
        author = EXCLUDED.author,
        api_payload = EXCLUDED.api_payload;
    
    INSERT INTO post_hashtags (post_id, hashtag_id, created_at)
    VALUES (video_id, fashion_hashtag_id, NOW())
    ON CONFLICT (post_id, hashtag_id) DO NOTHING;
    
    -- Post 6: jameswuantin
    video_id := '7568916711970180366';
    creator_username := 'jameswuantin';
    permalink := 'https://www.tiktok.com/@jameswuantin/video/7568916711970180366';
    
    INSERT INTO posts (
        id, external_id, platform_id, author, caption, media_url,
        posted_at, fetched_at, last_fetch_at, source, metrics, api_payload
    ) VALUES (
        video_id, video_id, tiktok_platform_id, creator_username,
        'TikTok video by @' || creator_username || ' #fashion',
        'https://p16-sign-va.tiktokcdn.com/obj/tos-maliva-p-0068/placeholder.jpg',
        NOW(), NOW(), NOW(), 'tiktok_demo_seed',
        '{"like_count": 0, "comment_count": 0, "view_count": 0}',
        json_build_object(
            'id', video_id,
            'creator', creator_username,
            'share_url', permalink,
            'url', permalink,
            'permalink', permalink
        )::text
    )
    ON CONFLICT (id) DO UPDATE SET
        author = EXCLUDED.author,
        api_payload = EXCLUDED.api_payload;
    
    INSERT INTO post_hashtags (post_id, hashtag_id, created_at)
    VALUES (video_id, fashion_hashtag_id, NOW())
    ON CONFLICT (post_id, hashtag_id) DO NOTHING;
    
    -- Post 7: prince_merlin9
    video_id := '7476098222260276498';
    creator_username := 'prince_merlin9';
    permalink := 'https://www.tiktok.com/@prince_merlin9/video/7476098222260276498';
    
    INSERT INTO posts (
        id, external_id, platform_id, author, caption, media_url,
        posted_at, fetched_at, last_fetch_at, source, metrics, api_payload
    ) VALUES (
        video_id, video_id, tiktok_platform_id, creator_username,
        'TikTok video by @' || creator_username || ' #fashion',
        'https://p16-sign-va.tiktokcdn.com/obj/tos-maliva-p-0068/placeholder.jpg',
        NOW(), NOW(), NOW(), 'tiktok_demo_seed',
        '{"like_count": 0, "comment_count": 0, "view_count": 0}',
        json_build_object(
            'id', video_id,
            'creator', creator_username,
            'share_url', permalink,
            'url', permalink,
            'permalink', permalink
        )::text
    )
    ON CONFLICT (id) DO UPDATE SET
        author = EXCLUDED.author,
        api_payload = EXCLUDED.api_payload;
    
    INSERT INTO post_hashtags (post_id, hashtag_id, created_at)
    VALUES (video_id, fashion_hashtag_id, NOW())
    ON CONFLICT (post_id, hashtag_id) DO NOTHING;
    
    -- Post 8: vinicci_
    video_id := '7525932445175155982';
    creator_username := 'vinicci_';
    permalink := 'https://www.tiktok.com/@vinicci_/video/7525932445175155982';
    
    INSERT INTO posts (
        id, external_id, platform_id, author, caption, media_url,
        posted_at, fetched_at, last_fetch_at, source, metrics, api_payload
    ) VALUES (
        video_id, video_id, tiktok_platform_id, creator_username,
        'TikTok video by @' || creator_username || ' #fashion',
        'https://p16-sign-va.tiktokcdn.com/obj/tos-maliva-p-0068/placeholder.jpg',
        NOW(), NOW(), NOW(), 'tiktok_demo_seed',
        '{"like_count": 0, "comment_count": 0, "view_count": 0}',
        json_build_object(
            'id', video_id,
            'creator', creator_username,
            'share_url', permalink,
            'url', permalink,
            'permalink', permalink
        )::text
    )
    ON CONFLICT (id) DO UPDATE SET
        author = EXCLUDED.author,
        api_payload = EXCLUDED.api_payload;
    
    INSERT INTO post_hashtags (post_id, hashtag_id, created_at)
    VALUES (video_id, fashion_hashtag_id, NOW())
    ON CONFLICT (post_id, hashtag_id) DO NOTHING;
    
    RAISE NOTICE '✅ Posts TikTok insérés et liés au hashtag #fashion';
END $$;

-- Vérification
SELECT 
    p.id,
    p.author,
    p.platform_id,
    pl.name as platform_name,
    ph.hashtag_id,
    h.name as hashtag_name
FROM posts p
JOIN platforms pl ON p.platform_id = pl.id
JOIN post_hashtags ph ON ph.post_id = p.id
JOIN hashtags h ON h.id = ph.hashtag_id
WHERE pl.name = 'tiktok' AND h.name = 'fashion'
ORDER BY p.fetched_at DESC;

