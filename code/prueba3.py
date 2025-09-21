
import praw
import pandas as pd
import time
import os
from datetime import datetime

# Conexión a Reddit API
reddit = praw.Reddit(
    client_id="Zgb9StBnvOPFEGPJ22yLdA",
    client_secret="BLgLZTY1x5D7avpGC6kYZAZn1gZIJg",
    user_agent="webscrapping2:v1.0"
)

print(f"HARDCODED - Client ID: {reddit.config.client_id}")
print(f"HARDCODED - Client Secret: {reddit.config.client_secret[:10]}...")

# Crear carpeta output si no existe
output_dir = "../output"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Subreddits objetivo según la tarea
target_subreddits = ['news', 'technology', 'science']

# Listas para almacenar datos
all_posts = []
all_comments = []

print("🚀 Iniciando recolección de datos de Reddit...")
print("=" * 60)

try:
    # PASO 4: Recolectar posts de cada subreddit
    for subreddit_name in target_subreddits:
        print(f"\n📊 Procesando r/{subreddit_name}...")
        
        try:
            subreddit = reddit.subreddit(subreddit_name)
            print(f"Conectado a r/{subreddit.display_name}")
            
            # Obtener 20 posts hot
            posts = subreddit.hot(limit=20)
            subreddit_posts = []
            
            for post in posts:
                post_data = {
                    'subreddit': subreddit_name,
                    'title': post.title,
                    'score': post.score,
                    'num_comments': post.num_comments,
                    'id': post.id,
                    'url': post.url,
                    'created_utc': datetime.fromtimestamp(post.created_utc),
                    'author': str(post.author) if post.author else '[deleted]'
                }
                
                subreddit_posts.append(post_data)
                all_posts.append(post_data)
                
                print(f"  📝 {post.title[:50]}... (Score: {post.score}, Comments: {post.num_comments})")
            
            print(f"✅ Recolectados {len(subreddit_posts)} posts de r/{subreddit_name}")
            
            # PASO 5: Recolectar comentarios de los posts más relevantes
            # Ordenar posts por score y tomar los top 5 (para no saturar)
            relevant_posts = sorted(subreddit_posts, key=lambda x: x['score'], reverse=True)[:5]
            
            print(f"💬 Recolectando comentarios de los {len(relevant_posts)} posts más relevantes...")
            
            for post_data in relevant_posts:
                try:
                    # Obtener el post completo para acceder a comentarios
                    submission = reddit.submission(id=post_data['id'])
                    submission.comments.replace_more(limit=0)
                    
                    # Recolectar los primeros 5 comentarios
                    comments_collected = 0
                    for comment in submission.comments:
                        if comments_collected >= 5:
                            break
                            
                        if hasattr(comment, 'body') and comment.body and comment.body != '[deleted]':
                            comment_data = {
                                'post_id': post_data['id'],
                                'subreddit': subreddit_name,
                                'post_title': post_data['title'][:50] + "...",
                                'body': comment.body[:200] + "..." if len(comment.body) > 200 else comment.body,
                                'score': comment.score,
                                'author': str(comment.author) if comment.author else '[deleted]',
                                'created_utc': datetime.fromtimestamp(comment.created_utc)
                            }
                            
                            all_comments.append(comment_data)
                            comments_collected += 1
                    
                    print(f"    💭 {comments_collected} comentarios de: {post_data['title'][:30]}...")
                    
                except Exception as e:
                    print(f"    ⚠️ Error al obtener comentarios del post {post_data['id']}: {e}")
                
                # Pausa para evitar rate limiting
                time.sleep(1)
                
        except Exception as e:
            print(f"❌ Error al procesar r/{subreddit_name}: {e}")
            continue
        
        print(f"⏱️ Esperando 2 segundos antes del siguiente subreddit...")
        time.sleep(2)

    # PASO 6: Guardar los datos
    print(f"\n💾 Guardando datos en archivos CSV...")
    print("=" * 60)
    
    # Crear DataFrames
    posts_df = pd.DataFrame(all_posts)
    comments_df = pd.DataFrame(all_comments)
    
    # Guardar en CSV con timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    posts_filename = f"{output_dir}/reddit_posts_{timestamp}.csv"
    comments_filename = f"{output_dir}/reddit_comments_{timestamp}.csv"
    
    posts_df.to_csv(posts_filename, index=False, encoding='utf-8')
    comments_df.to_csv(comments_filename, index=False, encoding='utf-8')
    
    # RESUMEN FINAL
    print(f"🎉 ¡PROCESO COMPLETADO EXITOSAMENTE!")
    print("=" * 60)
    print(f"📊 ESTADÍSTICAS:")
    print(f"   • Posts recolectados: {len(all_posts)}")
    print(f"   • Comentarios recolectados: {len(all_comments)}")
    print(f"   • Subreddits procesados: {len(target_subreddits)}")
    print(f"\n📁 ARCHIVOS GENERADOS:")
    print(f"   • {posts_filename}")
    print(f"   • {comments_filename}")
    
    # Mostrar muestra de datos
    if not posts_df.empty:
        print(f"\n📋 MUESTRA DE POSTS (Top 3 por score):")
        top_posts = posts_df.nlargest(3, 'score')[['subreddit', 'title', 'score', 'num_comments']]
        for idx, row in top_posts.iterrows():
            print(f"   🔥 r/{row['subreddit']}: {row['title'][:40]}... (Score: {row['score']})")
    
    if not comments_df.empty:
        print(f"\n💬 MUESTRA DE COMENTARIOS (Top 3 por score):")
        top_comments = comments_df.nlargest(3, 'score')[['subreddit', 'body', 'score']]
        for idx, row in top_comments.iterrows():
            print(f"   💭 r/{row['subreddit']}: {row['body'][:40]}... (Score: {row['score']})")
    
    print(f"\n✅ Conexión exitosa - PRAW funcionando correctamente")
    
except KeyboardInterrupt:
    print(f"\n⏹️ Proceso interrumpido por el usuario")
except Exception as e:
    print(f"\n❌ Error general: {e}")
    print(f"Tipo de error: {type(e)}")

