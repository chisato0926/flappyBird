import pygame 
from pygame.locals import *
import random

#pygameを初期化
pygame.init()

#クロックのインスタンスを生成
clock=pygame.time.Clock()
#fpsを設定(1秒間に60フレームを描画)
fps=60

#ゲーム画面の横幅
screen_width=864
#ゲーム画面の縦幅
screen_height=936

#ゲーム画面を生成
screen=pygame.display.set_mode((screen_width, screen_height))

#ゲームのタイトル名を設定
pygame.display.set_caption('Flappy Bird')

#スコア表示の文字フォントを設定
font=pygame.font.SysFont('Bauhaus 93', 60)

#文字の色を白色に設定
white=(255, 255, 255)

#変数を設定
ground_scroll=0 #地面のスクロールを管理
scroll_speed=4 #スクロールの速さ
flying=False #飛行中かどうかのフラグ
game_over=False #ゲームオーバーのフラグ
pipe_gap=350 #土管の距離
pipe_frequency=1500 #土管の頻度
last_pipe=pygame.time.get_ticks() - pipe_frequency #最後の土管
score=0 #スコア
pass_pipe=False #土管の通過フラグ

#背景、地面、リスタートボタンの画像をロード
bg=pygame.image.load("images/bg.png")
ground_img=pygame.image.load("images/ground.png")
button_img=pygame.image.load("images/restart.png")

#文字を描画する関数
def draw_text(text, font, text_col, x, y):
    img=font.render(text, True, text_col)
    screen.blit(img, (x, y))

#ゲームをリセットする関数
def reset_game():
    pipe_group.empty()
    #鳥をスタートの位置に戻す
    flappy.rect.x=100
    flappy.rect.y=int(screen_width/2)
    #スコアを0に戻す
    score=0
    return score

#鳥クラス
class Bird(pygame.sprite.Sprite):
    #初期化関数、インスタンス生成時に呼ばれる関数
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.images=[] #鳥の画像が入ったリスト
        self.index=0 #画像index
        self.counter=0 #カウンター

        #3枚の画像をリストに入れる
        for num in range(1,4):
            img=pygame.image.load(f'images/bird{num}.png')
            self.images.append(img)

        #インデックスを指定して画像を取得
        self.image=self.images[self.index]
        self.rect=self.image.get_rect() #画像を囲む四角形を取得
        self.rect.center=[x,y] #画像を囲む四角形の中央を指定した座標位置にする
        self.vel=0 #速度
        self.clicked=False #クリックのフラグ

    #更新関数　フレーム毎に実行
    def update(self):

        #飛行中なら
        if flying==True:
            self.vel+=0.5 #速度が増加。下に落ちる
            #速度が一定速度以上になったら
            if self.vel>8:
                self.vel=8 #最高速度以上には上がらない

            #鳥が地面の上にいるなら
            if self.rect.bottom<768:
                self.rect.y+=int(self.vel) #鳥のy座標の分だけ増加

        #ゲームオーバーになっていないなら
        if game_over==False:
            #マウスをクリックしたら
            if pygame.mouse.get_pressed()[0]==1 and self.clicked==False:
                self.clicked=True #クリックフラグを更新
                self.vel=-10 #速度は減少。上に飛ぶ。ゲーム内のY座標は上が負。

            #マウス左クリックを離したら
            if pygame.mouse.get_pressed()[0]==0:
                self.clicked=False #クリックフラグを更新

            self.counter+=1 #カウンター増加
            flap_cooldown=5 #羽ばたきをクールダウン

            #カウンターがクールダウン変数より大きくなったら
            if self.counter>flap_cooldown:
                self.counter=0 #カウンターを0に戻す
                self.index+=1 #画像indexを増加
                #画像indexが画像の枚数よりも大きくなったら
                if self.index>=len(self.images):
                    self.index=0 #画像indexを0に戻す

                #インデックスを用いて画像を指定
                self.image=self.images[self.index]

                #画像を傾ける
                self.image=pygame.transform.rotate(self.images[self.index], self.vel*-2)
        else:
            #ゲームオーバーになったら、鳥の向きは-90度回転。真下に落ちているように見える。
            self.image=pygame.transform.rotate(self.images[self.index], -90)

#土管クラス
class Pipe(pygame.sprite.Sprite):
    #初期化関数、インスタンス生成時に呼ばれる関数
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image=pygame.image.load("images/pipe.png") #土管画像をロード
        self.rect=self.image.get_rect() #土管画像を囲む四角形を取得

        #position=1の時は上の土管
        if position==1:
            self.image=pygame.transform.flip(self.image, False, True) #土管の画像を上下反転させる
            self.rect.bottomleft=[x, y-int(pipe_gap/2)] #隙間を考慮して配置

        #position=-1の時は下の土管
        if position==-1:
            self.rect.topleft=[x, y+int(pipe_gap/2)] #隙間を考慮して配置

    #更新関数　フレーム毎に実行
    def update(self):
        self.rect.x-=scroll_speed #スクロールスピードの分だけx座標を動かす。
        
        #土管の右端がゲーム画面左端に消えたらkillして削除。
        if self.rect.right<0:
            self.kill()

class Button():
    #初期化関数、インスタンス生成時に呼ばれる関数
    def __init__(self, x, y, image):
        self.image=image #画像を入れる変数
        self.rect=self.image.get_rect() #ボタン画像を囲む四角形
        self.rect.topleft=(x, y) #ボタンの左上の座標を指定

    #描画関数
    def draw(self):
        action=False #アクションフラグ
        pos=pygame.mouse.get_pos() #マウスの座標

        #ボタンのクリック判定。
        if self.rect.collidepoint(pos):
            #マウスをクリックした状態なら
            if pygame.mouse.get_pressed()[0]==1:
                action=True #アクションフラグを更新

        #指定の場所にボタンを描画
        screen.blit(self.image, (self.rect.x, self.rect.y))
        #アクションフラグを返す
        return action

#鳥のスプライト画像のグループ
bird_group=pygame.sprite.Group()
#土管のスプライト画像のグループ
pipe_group=pygame.sprite.Group()

#鳥のインスタンス
flappy=Bird(100, int(screen_height/2))

#鳥グループに鳥インスタンスを追加
bird_group.add(flappy)

#ボタンのインスタンス
button=Button(screen_width//2-50, screen_height//2-100, button_img)


#ゲームの実行フラグ
run=True

#ゲームが実行中
while run:
    #指定したfpsで描画
    clock.tick(fps)
    
    #背景を描画
    screen.blit(bg, (0, 0))

    #鳥をゲーム画面に描画
    bird_group.draw(screen)
    #鳥を更新
    bird_group.update()

    #土管をゲーム画面に描画
    pipe_group.draw(screen)

    #地面の画像を描画
    screen.blit(ground_img, (ground_scroll, 768))

    #土管の数が0以上なら
    if len(pipe_group)>0:
        #鳥の左端の座標が土管の左端より大きい、かつ、鳥の右端の座標が土管の右端の画像より小さい、かつ、通過フラグがFalse
        if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right and pass_pipe == False:
            pass_pipe=True #通過フラグを更新

        #通過フラグがTrueなら
        if pass_pipe==True:
            #鳥の画像の左端の座標が土管の右端の座標よりも大きいなら
            if bird_group.sprites()[0].rect.left>pipe_group.sprites()[0].rect.right:
                score+=1 #スコアを加算
                pass_pipe=False #通過フラグをFalseに戻す

    #スコアを描画
    draw_text(str(score), font, white, int(screen_width/2), 20)

    #鳥と土管の衝突判定、または、鳥の上部が画面外にある
    if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top<0:
        game_over=True #ゲームオーバーフラグを更新

    #鳥の下端が地面より下
    if flappy.rect.bottom>768:
        game_over=True #ゲームオーバーフラグを更新
        flying=False #飛行終了

    #ゲームオーバーでない、かつ、飛行中
    if game_over==False and flying==True:

        #時間を取得
        time_now=pygame.time.get_ticks()

        #最後に出現した土管から一定の時間が経っていたら
        if time_now-last_pipe>pipe_frequency:
            #-100~100のランダムな整数
            pipe_height=random.randint(-100, 100)
            #下の土管を配置
            btm_pipe=Pipe(screen_width, int(screen_height/2)+pipe_height, -1)
            #上の土管を配置
            top_pipe=Pipe(screen_width, int(screen_height/2)+pipe_height, 1)
            #土管グループに下の土管を追加
            pipe_group.add(btm_pipe)
            #土管グループに上の土管を追加
            pipe_group.add(top_pipe)
            #最後に出現した土管の時間を更新
            last_pipe=time_now

        #地面のスクロール変数を更新
        ground_scroll-=scroll_speed
    
        #地面のスクロール変数の絶対値が35以上になったら
        if abs(ground_scroll)>35:
            ground_scroll=0 #地面のスクロール変数を0に戻す

        #土管を更新
        pipe_group.update()

    #ゲームオーバーなら
    if game_over==True:
        #リスタートボタンを押したなら
        if button.draw()==True:
            game_over=False #ゲームオーバーフラグを戻す
            score=reset_game() #ゲームをリセット

    for event in pygame.event.get():
        #ゲーム終了のためのキー操作
        if event.type==pygame.QUIT:
            run=False

        #マウスをクリックすると飛行する
        if event.type==pygame.MOUSEBUTTONDOWN and flying==False and game_over==False:
            flying=True

    #ゲーム画面を更新
    pygame.display.update()

#ゲームを終了
pygame.quit()
