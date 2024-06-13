import cv2 
import mediapipe as mp 
import math 
import tkinter as tk 
import random 
import numpy as np
import time
from tkinter import Label, Button 
from PIL import Image, ImageTk   

from janken import * 

class VideoCaptureApp: 
    def __init__(self, window, window_title): 
        self.window = window 
        self.window.title(window_title) 
        self.video_source = 0 
        self.vid = cv2.VideoCapture(self.video_source) #將攝影機影像投放在畫布上
        self.canvas = tk.Canvas(window, width=self.vid.get(cv2.CAP_PROP_FRAME_WIDTH), 
                                height=self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)) 
        self.canvas.pack() 
 
        self.btn_frame = tk.Frame(window) 
        self.btn_frame.pack(side=tk.TOP, anchor=tk.NE) 
 
        # start button 
        self.start_button = Button(self.btn_frame, text="開始", command=self.start) 
        self.start_button.pack(side=tk.LEFT)  
        
        # win button 
        self.win_button = Button(self.btn_frame, text="會贏1局!", command=self.win) 
        self.win_button.pack(side=tk.LEFT) 
        
        # lose button 
        self.win_button = Button(self.btn_frame, text="會輸1局!", command=self.lose) 
        self.win_button.pack(side=tk.LEFT) 
 
        # new game button 
        self.new_game_button = Button(self.btn_frame, text="連續3局", command=self.new_game) 
        self.new_game_button.pack(side=tk.LEFT) 
        
        # finish button 
        self.quit_button = Button(self.btn_frame, text="離開", command=window.quit) 
        self.quit_button.pack(side=tk.LEFT)
 
        # 圖片下的文字區域和按鈕 
        self.info_frame = tk.Frame(window) 
        self.info_frame.pack(side=tk.BOTTOM, fill=tk.X) 
 
        self.text_label = Label(self.info_frame, text="歡迎來到拳魂", font=('Arial', 20, 'bold')) 
        self.text_label.pack(side=tk.LEFT) 
        
        self.countdown_label = Label(self.info_frame, text="")
        self.countdown_label.pack(side=tk.LEFT)
        
        self.result_txt = Label(self.info_frame, text="")
        self.result_txt.pack(side=tk.BOTTOM)
        
        self.images = ["img/janken_stone.png", "img/janken_scissor.png", "img/janken_paper.png"]
        self.janken_categories = ["石頭", "剪刀", "布"]
        self.gamer_choice = 3 # 初始化玩家猜拳
        self.computer_choice = random.randint(0, 2) #幫電腦先隨機一個
        self.selected_image_path = self.images[self.computer_choice]
 
        self.image = Image.open(self.selected_image_path) 
        self.image = self.image.resize((100, 100)) 
        self.image_tk = ImageTk.PhotoImage(self.image) 
        self.image_label = Label(self.info_frame, image=self.image_tk) 
        self.image_label.pack(side=tk.LEFT) 
 
        self.delay = 15 
        self.is_running = False # 開啟相機設定
        self.winnerflag = False # 必贏flag
        self.loseflag = False # 必輸flag
        
        # 剪刀石頭布手部偵測設定
        self.mp_drawing = mp.solutions.drawing_utils 
        self.mp_hands = mp.solutions.hands 
        self.fontFace = cv2.FONT_HERSHEY_SIMPLEX 
        self.lineType = cv2.LINE_AA 
 
        self.hands = self.mp_hands.Hands( 
            model_complexity=0, 
            min_detection_confidence=0.5, 
            min_tracking_confidence=0.5) 
 
        self.update() 
        self.window.mainloop() 
 
    def start(self): 
        self.game_num = 1
        self.countdown_time = 5  
        self.update_countdown()
        self.is_running = True 
 
    def update(self): 
        if self.is_running: 
            ret, frame = self.vid.read() 
            if ret: 
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) 
                results = self.hands.process(frame_rgb) 
                if results.multi_hand_landmarks: 
                    for hand_landmarks in results.multi_hand_landmarks: 
                        finger_points = [] 
                        for i in hand_landmarks.landmark: 
                            x = int(i.x * frame.shape[1]) 
                            y = int(i.y * frame.shape[0]) 
                            finger_points.append((x, y)) 
                        if finger_points: 
                            finger_angle = hand_angle(finger_points) 
                            text = hand_pos(finger_angle)
                            if(text == 'stone'):
                                self.gamer_choice = 0
                            elif(text == 'scissors'):
                                self.gamer_choice = 1
                            elif(text == 'paper'):
                                self.gamer_choice = 2
                            # 在畫面上顯示你出了什麼
                            cv2.putText(frame, text, (30, 120), self.fontFace, 1, (255, 255, 255), 2, self.lineType) 
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) 
                self.photo = ImageTk.PhotoImage(image=Image.fromarray(frame)) 
                self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW) 
 
        self.window.after(self.delay, self.update) 
 
    def new_game(self): 
        # 倒數計時 
        self.game_num = 3
        self.countdown_time = 5  
        self.update_countdown()
        
    def win(self):
        # 倒數計時 
        self.game_num = 1
        self.countdown_time = 5 
        self.update_countdown()
        self.winnerflag = True
        
    def lose(self):
        self.game_num = 1
        self.countdown_time = 5 
        self.update_countdown()
        self.loseflag = True
 
    def __del__(self): 
        if self.vid.isOpened(): 
            self.vid.release() 
        self.hands.close()
    
    def update_countdown(self):
        if self.countdown_time > 0:
            self.countdown_label.config(text=f"倒計時: {self.countdown_time} 秒")
            self.countdown_time -= 1
            self.window.after(1000, self.update_countdown)
        else:
            # 不管怎麼樣都先隨機
            self.computer_choice = random.randint(0, 2)
            # 如果有必贏flag，則會自動選取我們贏
            if(self.winnerflag == True):
                if self.gamer_choice == 0:
                    self.computer_choice = 1
                elif (self.gamer_choice == 1):
                    self.computer_choice = 2
                elif (self.gamer_choice == 2):
                    self.computer_choice = 0
                else:
                    self.result = "，你根本沒出"

            # 如果有必輸flag，則會自動選則讓我們輸
            if(self.loseflag == True):
                if self.gamer_choice == 1:
                    self.computer_choice = 0
                elif (self.gamer_choice == 2):
                    self.computer_choice = 1
                elif (self.gamer_choice == 0):
                    self.computer_choice = 2
                else:
                    self.result = "，你根本沒出"
                    
            self.winnerflag = False
            self.loseflag = False
            # 將圖片放到畫布上
            self.selected_image_path = self.images[self.computer_choice]
            self.image = Image.open(self.selected_image_path) 
            self.image = self.image.resize((100, 100)) 
            self.image_tk = ImageTk.PhotoImage(self.image) 
            self.image_label.configure(image=self.image_tk) 
            self.image_label.image = self.image_tk

            # 判斷輸贏
            if self.gamer_choice in [0, 1, 2]:
                if self.gamer_choice == self.computer_choice:
                    self.result = "，平手"
                elif (self.gamer_choice == 0 and self.computer_choice == 1) or \
                    (self.gamer_choice == 1 and self.computer_choice == 2) or \
                    (self.gamer_choice == 2 and self.computer_choice == 0):
                    self.result = "，你贏了!"
                else:
                    self.result = "，你輸了!"
            else:
                self.result = "，你根本沒出"
            self.result_txt.config(text="你在最後一刻出了"+self.janken_categories[self.gamer_choice]+"，電腦出的是"+self.janken_categories[self.computer_choice]+self.result)
            self.countdown_label.config(text="倒計時: 0 秒")
            self.game_num -= 1
            if (self.game_num > 0):
                self.countdown_time = 5 
                self.update_countdown() 
            
if __name__ == "__main__":
    root = tk.Tk()
    app = VideoCaptureApp(root, "janken")
    
