#UnoGame
#add ready screen for multiple human players, differing AI, stacking, house rules (teams)
#Add to Github

import operator 
import re #reg expressions
import random, pygame, sys
from pygame.locals import *
import os.path

FPS = 30 # frames per second
TABLEWIDTH = 20 # number of columns of cards
TABLEHEIGHT = 10 # number of rows of cards
CARDWIDTH = 48 #96
CARDHEIGHT = 72#144 
GAPSIZE = 5 
WINDOWWIDTH = TABLEWIDTH*CARDWIDTH+(TABLEWIDTH+1)*GAPSIZE
WINDOWHEIGHT = 670 

SCREEN = None

COLORWIDTH=WINDOWWIDTH/5
COLORHEIGHT=WINDOWHEIGHT/20
COLORGAP=GAPSIZE*2
COLORTABLEWIDTH = 5
COLORTABLEHEIGHT = 15

SORTMETHOD = '' #name,color, unsorted

RED	     = (255,   0,   0)
GREEN  	 = (  0, 170,   0)
BLUE	 = (  0,   0, 255)
YELLOW   = (255, 200,   0)

WHITE = (255,255,255)

FPSCLOCK = pygame.time.Clock()

colorDic = {'red' : 0, 'green' : 1, 'blue' :2, 'yellow' : 3, 'none' : 4, 'wild':4,
		0:'red',1:'green',2:'blue',3:'yellow',4:'none'}
nameDic = {'0':0,'1':1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'reverse':10,'skip':11,'draw two':12,'draw 2':12,'wild':13,'wild draw four':14,'wild draw 4':14,'draw four':14,'draw 4':14,
		 0:'0',1:'1',2:'2',3:'3',4:'4',5:'5',6:'6',7:'7',8:'8',9:'9',10:'reverse',11:'skip',12:'draw two',13:'wild',14:'wild draw four'}

def main():	
	deck = Deck([])
	discardPile = Deck([])
	players = []
	turn,direction = 0,1
		
	pattern = '^[0-4]$'
	
	humanPlayerStr=''
	AIPlayerStr=''
	
	while None is re.match(pattern,humanPlayerStr):
		humanPlayerStr=input("Input number of human players (0-4): ").strip()
	humanPlayerNum = int(humanPlayerStr)
	
	for i in range(humanPlayerNum):
		s = input("Input Player " + str(i+1) + "'s name: " ).strip()
		players.append(HumanPlayer(s,[]))
	
	while None is re.match(pattern,AIPlayerStr):
		AIPlayerStr = input("Input number of AI players (0-4): ").strip()
	AIPlayerNum = int(AIPlayerStr)
	for i in range(AIPlayerNum):
		players.append(AIPlayer("AI Player " + str(i+1),[]))
	
	global SORTMETHOD
	while None is re.match('^(?:color|name|num|number|none|unsorted)$',SORTMETHOD):
		SORTMETHOD = input("Sort by color, name, or none: ").lower().strip()
	
	
	playerNum = humanPlayerNum+AIPlayerNum 
				
	deck.fillDeck()
	deck.shuffle()
	discardPile.add(deck.remove())
	if nameDic[discardPile.getTopCard().name] >=13: # if wild, selects color at random
		n = discardPile.getTopCard().name
		c = random.randint(0,3)
		discardPile.setTopCard(Card(c,n))
	for i in range(playerNum):
		players[i].fillHand(deck)	
		
	global SCREEN 
	SCREEN = pygame.display.set_mode((WINDOWWIDTH,WINDOWHEIGHT))
	pygame.init()
	pygame.display.set_caption('UNO!')
	mousex = 0
	mousey = 0
	
	printCards(players,discardPile,turn)	
	gameOver=False
	cardPlayed=True
	while True: 
		mouseClicked = False
		temp=turn
						
		for event in pygame.event.get(): 
			if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
				pygame.quit()
				sys.exit()
			elif event.type == MOUSEMOTION:				
				mousex, mousey = event.pos
			elif event.type == MOUSEBUTTONUP:
				mousex, mousey = event.pos
				mouseClicked = True
		
		cardx, cardy, cardSelect = getCardAtPixel(mousex, mousey,players,discardPile)		
		SCREEN.fill((0,0,0))		
		
		
		if cardPlayed==True: #***********
			if cardx != None and cardy != None and cardSelect is not None and isinstance(players[turn], HumanPlayer):# cardSelect != Card('none',0):
				if cardSelect == Card('none',0):
					drawHighlightCard(cardx, cardy,BLUE)													
				elif cardy == turn:
					if cardSelect.isPlayable(discardPile.getTopCard()):
						drawHighlightCard(cardx, cardy,GREEN)
					else:
						drawHighlightCard(cardx, cardy,RED)	
									
			if mouseClicked==True:			
				if len(deck)==0:  			#Check if deck needs refilling
					if len(discardPile)==0: #No cards in deck or discard pile
						quit()
					deck.refill(discardPile)
				if isinstance(players[turn],HumanPlayer):
					card = players[turn].go(deck,discardPile,players,turn,cardSelect) 
				elif isinstance(players[turn],AIPlayer):
					temp = getNextTurn(turn,playerNum,direction)
					nextCardNum = len(players[temp])
					card = players[turn].go(deck,discardPile,nextCardNum)  #Return card to see what card was played (rev,skip,etc.)
				
				if (card is not None):		               #If successful play			
					if (not card.__eq__(Card('none',0))):
						if (card.name == 'reverse'):
							direction = -direction			
						elif (card.name == 'skip'):
							turn=getNextTurn(turn,playerNum,direction)
						elif (card.name == 'draw two'):
							next=getNextTurn(turn,playerNum,direction)
							players[next].draw(deck)
							players[next].draw(deck)
						elif (card.name == 'wild draw four'):
							next=getNextTurn(turn,playerNum,direction)
							players[next].draw(deck)
							players[next].draw(deck)
							players[next].draw(deck)
							players[next].draw(deck)						
					temp=getNextTurn(turn,playerNum,direction)
					cardPlayed=False
					printBackCards(players,discardPile,turn)
							
				for p in players:  #If winner
					if len(p) ==0:
						gameOver = True		
						
		
			if (gameOver ==True):
				pygame.display.update()	
				break
			elif turn != temp:		
				turn=temp	
			else:
				printCards(players,discardPile,turn)
				pygame.display.update()			
				FPSCLOCK.tick(FPS)					
		else:							
			printBackCards(players,discardPile,turn)
			pygame.display.update()			
			FPSCLOCK.tick(FPS)		
			if mouseClicked:	
				cardPlayed=True
						
	
	while True:#After Game over   (below is the glorious flashing Comic Sans)
		myfont = pygame.font.SysFont("Comic Sans MS", 100)	
		label = myfont.render(players[turn].name + " wins!!!", 1, RED)
		SCREEN.blit(label, (300, 250))
		pygame.display.update()	
		FPSCLOCK.tick(10)		
		label = myfont.render(players[turn].name + " wins!!!", 1, GREEN)
		SCREEN.blit(label, (300, 250))
		pygame.display.update()	
		FPSCLOCK.tick(10)			
		label = myfont.render(players[turn].name + " wins!!!", 1, BLUE)
		SCREEN.blit(label, (300, 250))
		pygame.display.update()	
		FPSCLOCK.tick(10)	
		label = myfont.render(players[turn].name + " wins!!!", 1, YELLOW)
		SCREEN.blit(label, (300, 250))
		pygame.display.update()	
		FPSCLOCK.tick(10)	
		for event in pygame.event.get():
			if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE) or event.type == MOUSEBUTTONUP:
				pygame.quit()
				sys.exit()
				
def getNextTurn(turn,playerNum,direction):
	temp = turn+direction
	if(temp>=playerNum):
		temp=0
	if(temp<0):
		temp=playerNum-1
	return temp
				
def printCards(players,discardPile,turn):			
	i,j,k=GAPSIZE,GAPSIZE,0		
	oneHuman=False
	allAI=False
	if isinstance(players[1], AIPlayer):
		oneHuman=True
	if isinstance(players[0], AIPlayer):
		allAI=True
	for p in players:		
		if k == turn:
			pygame.draw.rect(SCREEN, GREEN, (0,j,GAPSIZE,CARDHEIGHT), 0)
		pic = pygame.image.load(os.path.join('Pics','back.png'))
		pic = pygame.transform.scale(pic, (CARDWIDTH,CARDHEIGHT))	
		if len(p.list) > TABLEWIDTH-2: #If too many, just print playables					
			if k==turn and isinstance(players[turn], HumanPlayer) or (k==0 and oneHuman) or allAI:
				for c in p.getPlayable(discardPile):					
					pic = pygame.transform.scale(c.image, (CARDWIDTH,CARDHEIGHT)) #change card size
					SCREEN.blit(pic, (i, j))								
					i+=CARDWIDTH+GAPSIZE
			else:
				for num in range(TABLEWIDTH-2):
					SCREEN.blit(pic, (i, j))								
					i+=CARDWIDTH+GAPSIZE
				
				
			myfont = pygame.font.SysFont("Arial", 10)			
			a,b = leftTopCoordsOfCard(TABLEWIDTH-2, j)
			b=j
			
			label = myfont.render("Number of Cards: " + str(len(p)), 1, WHITE)
			SCREEN.blit(label, (a,b))
			b+=10
			i=0
			if k == turn and isinstance(players[turn], HumanPlayer) or (k==0 and oneHuman) or allAI:
				for c in p.list: 
					if i > 12 and i%13==0:	
						a+=CARDWIDTH/4
						b=j+10
					label = myfont.render(c.getShortName(), 1, c.getColorValue())
					SCREEN.blit(label, (a,b))
					b+=10
					i+=1
		else:			
			for c in p.list:					
				if k==turn and isinstance(players[turn], HumanPlayer) or (k==0 and oneHuman) or allAI:
					pic = pygame.transform.scale(c.image, (CARDWIDTH,CARDHEIGHT)) #change card size				
				SCREEN.blit(pic, (i, j))								
				i+=CARDWIDTH+GAPSIZE						
		j+= CARDHEIGHT+GAPSIZE
		i=GAPSIZE
		k+=1

	pic = pygame.image.load(os.path.join('Pics','back.png')) #main deck
	pic = pygame.transform.scale(pic, (CARDWIDTH,CARDHEIGHT))
	SCREEN.blit(pic, (WINDOWWIDTH-CARDWIDTH-GAPSIZE, GAPSIZE)) 
	pic = pygame.transform.scale(discardPile.getTopCard().image, (CARDWIDTH,CARDHEIGHT))#discard pile
	SCREEN.blit(pic, (WINDOWWIDTH-CARDWIDTH-GAPSIZE, GAPSIZE+CARDHEIGHT+GAPSIZE))	
		
def printBackCards(players,discardPile,turn):	
	
	i,j,k=GAPSIZE,GAPSIZE,0		
	for p in players:		
		if k == turn:
			pygame.draw.rect(SCREEN, GREEN, (0,j,GAPSIZE,CARDHEIGHT), 0)
		pic = pygame.image.load(os.path.join('Pics','back.png'))
		pic = pygame.transform.scale(pic, (CARDWIDTH,CARDHEIGHT))	
		if len(p.list) > TABLEWIDTH-2: #If too many, just print playables					
			for num in range(TABLEWIDTH-2):
				SCREEN.blit(pic, (i, j))								
				i+=CARDWIDTH+GAPSIZE				
				
			myfont = pygame.font.SysFont("Arial", 10)			
			a,b = leftTopCoordsOfCard(TABLEWIDTH-2, j)
			b=j
			
			label = myfont.render("Number of Cards: " + str(len(p)), 1, WHITE)
			SCREEN.blit(label, (a,b))			
			
		else:			
			for c in p.list:											
				SCREEN.blit(pic, (i, j))								
				i+=CARDWIDTH+GAPSIZE						
		j+= CARDHEIGHT+GAPSIZE
		i=GAPSIZE
		k+=1

	pic = pygame.image.load(os.path.join('Pics','back.png')) #main deck
	pic = pygame.transform.scale(pic, (CARDWIDTH,CARDHEIGHT))
	SCREEN.blit(pic, (WINDOWWIDTH-CARDWIDTH-GAPSIZE, GAPSIZE)) 
	pic = pygame.transform.scale(discardPile.getTopCard().image, (CARDWIDTH,CARDHEIGHT))#discard pile
	SCREEN.blit(pic, (WINDOWWIDTH-CARDWIDTH-GAPSIZE, GAPSIZE+CARDHEIGHT+GAPSIZE))	

def getCardAtPixel(x,y,players,discardPile):
	for cardx in range(TABLEWIDTH):
		for cardy in range(TABLEHEIGHT):
			left, top = leftTopCoordsOfCard(cardx, cardy)
			cardRect = pygame.Rect(left, top, CARDWIDTH, CARDHEIGHT)
			if cardRect.collidepoint(x, y):
				c = Card('none',0)
				c = getCardAtLocation(cardx,cardy,players,discardPile)
				return (cardx, cardy,c)
	return (None, None,Card('none',0))
	
def getCardAtLocation(cardx,cardy,players,discardPile):	
	if cardy >= len(players):
		return None
	if cardx == (TABLEWIDTH-1) and cardy==0:
		return  Card('none',0)
	elif cardx >= len(players[cardy]):
		return None
	
	i=0
	if len(players[cardy].list) < TABLEWIDTH-1:
		for c in players[cardy].list:
			if i==cardx:
				return c
			i+=1
	else:
		for c in players[cardy].getPlayable(discardPile):
			if i==cardx:
				return c
			i+=1
	
def leftTopCoordsOfCard(cardx, cardy):	
	left = cardx * (CARDWIDTH + GAPSIZE) + GAPSIZE
	top = cardy * (CARDHEIGHT + GAPSIZE) + GAPSIZE
	return (left, top)
	
def drawHighlightCard(cardx, cardy,color):
	left, top = leftTopCoordsOfCard(cardx, cardy)
	pygame.draw.rect(SCREEN, color, (left - 2, top - 2, CARDWIDTH + 4, CARDHEIGHT + 4), 0)
	
def printColorSelect():
	pygame.draw.rect(SCREEN, RED,   (COLORGAP,                WINDOWHEIGHT-COLORHEIGHT-3*COLORGAP/2-2, COLORWIDTH, COLORHEIGHT), 0)
	pygame.draw.rect(SCREEN, GREEN, (COLORGAP*2+COLORWIDTH,   WINDOWHEIGHT-COLORHEIGHT-3*COLORGAP/2-2, COLORWIDTH, COLORHEIGHT), 0)
	pygame.draw.rect(SCREEN, BLUE,  (COLORGAP*3+COLORWIDTH*2, WINDOWHEIGHT-COLORHEIGHT-3*COLORGAP/2-2, COLORWIDTH, COLORHEIGHT), 0)
	pygame.draw.rect(SCREEN, YELLOW,(COLORGAP*4+COLORWIDTH*3, WINDOWHEIGHT-COLORHEIGHT-3*COLORGAP/2-2, COLORWIDTH, COLORHEIGHT), 0)
	
def getColorAtPixel(x,y):
	for colorx in range(COLORTABLEWIDTH):
		for colory in range(COLORTABLEHEIGHT):
			left, top = leftTopCoordsOfColor(colorx, colory)
			colorRect = pygame.Rect(left, top, COLORWIDTH, COLORHEIGHT)
			if colorRect.collidepoint(x, y):
				c = Color(0,0,0)
				c = getColorAtLocation(colorx,colory)
				return (colorx, colory,c)
	return (None, None,None)
		
def leftTopCoordsOfColor(colorx,colory):
	top = colory * (COLORHEIGHT + COLORGAP) + COLORGAP
	left = colorx * (COLORWIDTH + COLORGAP) + COLORGAP	
	return (left, top)
	
def getColorAtLocation(colorx,colory):	
	if colory != COLORTABLEHEIGHT-1:
		return None
	elif colorx >= COLORGAP*4+COLORWIDTH*4:		
		return None
	i=0
	colors = [RED,GREEN,BLUE,YELLOW]
	for c in colors:
		if i==colorx:
			return colors[i]
		i+=1
	
def drawHighlightColor(colorx,colory,color):
	left, top = leftTopCoordsOfColor(colorx,colory)
	pygame.draw.rect(SCREEN, color, (left - 5, top - 5, COLORWIDTH+10, COLORHEIGHT+10), 0)
	
'''----------------------------------------------------------------------------------------------------------------------------------------------------'''		 
class Card(object):
	def __init__(self,color,name):
		if isinstance(color, str):
			color = colorDic[color.lower()]
		if isinstance(name, str):
			name = nameDic[name.lower()]	
		self.colorInt = color
		self.nameInt = name
		self.color = colorDic[color]
		self.name = nameDic[name]
		
		self.tuple=(self.color,self.name)
		self.tupleInt=(self.colorInt,self.nameInt)		
		self.image = pygame.image.load(os.path.join('Pics', self.__str__()+'.png'))
						
	def __str__(self):
		if(colorDic[self.color] !=4):			
			return self.color + ' ' + self.name
		else:
			return self.name
		
	def isPlayable(self,other):
		return self.nameInt>=nameDic['wild'] or self.color==other.color or self.name==other.name 	
		
	def __eq__(self, other):
		if self is not None and other is not None:
			return (self.color == other.color) and (self.name==other.name)
			
	def __lt__(self, other):
		i = self.nameInt-other.nameInt
		if i ==0:
			return self.colorInt-other.colorInt<0
		return i<0
		
	def getColorValue(self):
		stringToColor = {'red':RED,'green':GREEN,'blue':BLUE,'yellow':YELLOW,'none':WHITE}
		return stringToColor[self.color]
		
	def getShortName(self):
		if self.name == 'reverse':
			return 'rev'
		elif self.name == 'draw two':
			return 'draw 2'
		elif self.name == 'wild draw four':
			return 'draw 4'
		else:
			return self.name
		
class Deck(object):
	def __init__(self,list=[]):
		self.list=list
	
	def shuffle(self):
		random.shuffle(self.list)
		
	def remove(self):
		return self.list.pop()
	
	def getTopCard(self):
		return self.list[len(self.list)-1]
	
	def setTopCard(self,c):
		self.list[len(self.list)-1] = c
		
	def add(self,*args):
		for card in args:
			self.list.append(card)
		
	def __str__(self):
		s=''
		for card in self.list:
			s+=card.__str__()+'\n'
		return s
		
	def fillDeck(self):
		for i in range(0,13):
			for j in range(0,4):			
				self.list.append(Card(j,i))
				if i>0:
					self.list.append(Card(j,i))
		for i in range(13,15):
			for j in range(0,4):
				self.list.append(Card(4,i))
							
	def __len__(self):
		return len(self.list)	
		
	def refill(self,other): #self =deck, other=discardPile		
		temp=other.remove()
		for i in range(0,len(other)):
			c = other.remove()
			if 'wild' in c.name:
				c = Card('none',c.name)
			self.add(c)
		self.shuffle()
		other.add(temp)		
				
class Player(object):
	def __init__(self,name='Player',list=[]):
		self.name=name
		self.list=list
		
	def play(self,card,discardPile):
		topCard = discardPile.getTopCard()
		for c in self.list:
			if c == card: 
				if c.isPlayable(topCard):
					self.list.remove(card)
					discardPile.add(card)					
					return
				else:					
					return
					
	def add(self,*args):
		for card in args:
			self.list.append(card)
		self.sort()
		
	def __str__(self):
		s=self.name+':\n'
		for card in self.list:
			s+=card.__str__()+'  '
		return s
		
	def __contains__(self, card):
		return card in self.list
			
	def fillHand(self,deck):
		for i in range(0,7):
			self.list.append(deck.remove())
		self.sort()
	
	def draw(self,deck):
		if len(deck) ==0:			
			myfont = pygame.font.SysFont("Comic Sans MS", 100)	
			label = myfont.render("YOU ALL LOSE", 1, RED)
			SCREEN.blit(label, (300, 250))
			pygame.display.update()	
			pygame.time.wait(3000)
			quit()
		c = deck.remove()
		self.list.append(c)
		self.sort()		
	
	def __len__(self):
		return len(self.list)
		
	def sort(self):
		if(SORTMETHOD=='name' or SORTMETHOD=='num' or SORTMETHOD =='number'):
			self.list.sort(key=lambda x: x.colorInt)
			self.list.sort(key=lambda x: x.nameInt)
		elif(SORTMETHOD=='color'):
			self.list.sort(key=lambda x: x.nameInt)
			self.list.sort(key=lambda x: x.colorInt)
		else: #unsorted/sort by time drawn
			pass
	
	def chooseSort(self,method):
		if(method=='name' or method=='num'):
			self.list.sort(key=lambda x: x.colorInt)
			self.list.sort(key=lambda x: x.nameInt)
		elif(method=='color'):
			self.list.sort(key=lambda x: x.nameInt)
			self.list.sort(key=lambda x: x.colorInt)
		else: #unsorted/sort by time drawn
			pass
				
	def getPlayable(self,discardPile):
		topCard = discardPile.getTopCard()
		playables =[]
		for c in self.list:
			if (c.isPlayable(topCard)):
				playables.append(c)
		return playables	
		
	def getMostColor(self):
		r,g,b,y=0,0,0,0		
		for c in self.list:
			if c.colorInt == 0:
				r+=1
			elif c.colorInt == 1:
				g+=1			
			elif c.colorInt == 2:
				b+=1				
			elif c.colorInt == 3:
				y+=1
				
		if (r>=g and r>=b and r>=y):
			return 'red'
		elif (g>=b and g>=y):
			return 'green'
		elif (b>=y):
			return 'blue'
		else:
			return 'yellow'
		
class AIPlayer(Player):	
	def go(self,deck,discardPile,nextCardNum):
		topCard = discardPile.getTopCard()
		playables = self.getPlayable(discardPile)
		last = len(playables)-1
		if (last+1 <= 0):
			self.draw(deck)
			return Card('none',0)
		elif(nextCardNum > 2):
			self.play(playables[0],discardPile)	
			if('wild' in playables[0].name):
				c = self.getMostColor()
				n = playables[0].name
				discardPile.setTopCard(Card(c,n))
			return playables[0]
		else:
			self.play(playables[last],discardPile)	
			if('wild' in playables[last].name):
				c = self.getMostColor()
				n = playables[last].name
				discardPile.setTopCard(Card(c,n))
			return playables[last]
		
class HumanPlayer(Player):	
	def go(self,deck,discardPile,players,turn,card):		
		topCard = discardPile.getTopCard()
		playables = self.getPlayable(discardPile)		
		if (card == Card('none',0)): 
			self.draw(deck)		
			return Card('none',0)			
		elif (card) in playables:		#elif		
			self.play(card,discardPile)
			if card.name == 'wild' or card.name == 'wild draw four':
				mousex = 0 
				mousey = 0
				colorToString = {RED:'red',GREEN:'green',BLUE:'blue',YELLOW:'yellow'}
				n = card.name
				c= None				
				while True:
					mouseClicked=False
					for event in pygame.event.get():
						if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
							pygame.quit()
							sys.exit()
						elif event.type == MOUSEMOTION:				
							mousex, mousey = event.pos
						elif event.type == MOUSEBUTTONUP:
							mousex, mousey = event.pos
							mouseClicked = True
										
					colorx,colory,colorSelect = getColorAtPixel(mousex, mousey)					
					SCREEN.fill((0,0,0))		
					if colorx is not None and colory is not None and colorSelect is not None:
						drawHighlightColor(colorx, colory,colorSelect)					
					if mouseClicked == True and colorx is not None and colory is not None and colorSelect is not None:					
						c = colorToString[colorSelect]
						discardPile.setTopCard(Card(c,n))
						card = Card(c,n)
						break
					printCards(players,discardPile,turn)	
					printColorSelect()
					pygame.display.update()			
					FPSCLOCK.tick(FPS)	
			return (card)	
			
if __name__ == '__main__':
	main()