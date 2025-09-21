import praw

# Conexión que sabemos que funciona
reddit = praw.Reddit(
    client_id="6Wee48hceqsvGGXH_0ycTQ",
    client_secret="noonz-mMIKxE4X1kk7hTF4VGapuRoQ",
    user_agent="webscrapping2:v1.0"
)

print("🔍 TEST BÁSICO DE RECOLECCIÓN")
print("=" * 50)

try:
    # Test con un subreddit simple
    subreddit = reddit.subreddit("python")
    print(f"📊 Conectado a r/{subreddit.display_name}")
    
    # Intentar obtener posts
    posts = list(subreddit.hot(limit=5))
    print(f"🔢 Posts obtenidos: {len(posts)}")
    
    if len(posts) > 0:
        print("✅ Posts encontrados:")
        for i, post in enumerate(posts, 1):
            print(f"   {i}. {post.title[:50]}...")
            print(f"      ID: {post.id}")
            print(f"      Score: {post.score}")
            print(f"      Comments: {post.num_comments}")
            print(f"      URL: {post.url[:50]}...")
            print()
    else:
        print("❌ NO se encontraron posts")
        
except Exception as e:
    print(f"❌ ERROR: {e}")
    print(f"Tipo: {type(e)}")