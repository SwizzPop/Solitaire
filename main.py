from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import Rectangle, Color
from kivy.properties import ListProperty, NumericProperty, BooleanProperty
from kivy.core.image import Image as CoreImage
from kivy.uix.label import Label
from kivy.uix.popup import Popup
import random
import os
from database import GameDatabase
from time import time

class Card(Image):
    def __init__(self, source, pos, size=(100, 140), **kwargs):
        super().__init__(**kwargs)
        self.source = source
        self.pos = pos
        self.size = size
        self.allow_stretch = True
        self.keep_ratio = True
        self.texture = CoreImage(source, keep_data=True).texture

class CardGame(Widget):
    dealt_cards = ListProperty([])
    total_cards = NumericProperty(52)
    cards_in_deck = NumericProperty(52)
    autoplay_active = BooleanProperty(False)
    is_portrait = BooleanProperty(True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = GameDatabase()
        self.game_start_time = time()
        Window.bind(on_resize=self._on_window_resize)
        
        self.card_images = {}
        self.load_cards()
        
        # Set initial size and orientation
        self.size = Window.size
        self.pos = (0, 0)
        self.is_portrait = Window.height > Window.width
        
        self.setup_buttons()
        self.init_game()
        
        self.bind(size=self.update_card_positions)
        Clock.schedule_once(lambda dt: self.update_card_positions(), 0)

    def _on_window_resize(self, instance, width, height):
        self.size = (width, height)
        self.is_portrait = height > width
        self.setup_buttons()  # Recreate buttons for new orientation
        
    def setup_buttons(self):
        # Remove existing buttons and labels
        for child in self.children[:]:
            if isinstance(child, (Button, Label)):
                self.remove_widget(child)

        if self.is_portrait:
            self._setup_portrait_buttons()
        else:
            self._setup_landscape_buttons()

        self.stats_button = Button(
            text='Stats',
            size_hint=(None, None),
            size=(100, 50),
            pos_hint={'right': 0.95, 'top': 0.95}
        )
        self.stats_button.bind(on_press=self.show_stats)
        self.add_widget(self.stats_button)

    def _setup_portrait_buttons(self):
        button_width = Window.width * 0.1
        button_height = Window.height * 0.067
        button_y = Window.height * 0.033

        self.check_btn = Button(
            text='Check', 
            size_hint=(None, None),
            size=(button_width, button_height),
            pos=(Window.width * 0.16, button_y)
        )
        self.check_btn.bind(on_press=self.check_cards)
        self.add_widget(self.check_btn)

        self.redeal_btn = Button(
            text='Redeal',
            size_hint=(None, None),
            size=(button_width, button_height),
            pos=(Window.width * 0.28, button_y)
        )
        self.redeal_btn.bind(on_press=self.init_game)
        self.add_widget(self.redeal_btn)

        self.autoplay_btn = Button(
            text='Autoplay',
            size_hint=(None, None),
            size=(button_width, button_height),
            pos=(Window.width * 0.40, button_y)
        )
        self.autoplay_btn.bind(on_press=self.toggle_autoplay)
        self.add_widget(self.autoplay_btn)

        # Move cards label to the right of stats button
        self.cards_label = Label(
            text=f'Cards: {self.total_cards}',
            size_hint=(None, None),
            size=(Window.width * 0.15, Window.height * 0.067),
            pos=(Window.width * 0.85, Window.height * 0.95)  # Position to right of stats button
        )
        self.add_widget(self.cards_label)

    def _setup_landscape_buttons(self):
        button_width = Window.width * 0.06
        button_height = Window.height * 0.1
        button_x = Window.width * 0.92

        self.check_btn = Button(
            text='Check', 
            size_hint=(None, None),
            size=(button_width, button_height),
            pos=(button_x, Window.height * 0.7)
        )
        self.check_btn.bind(on_press=self.check_cards)
        self.add_widget(self.check_btn)

        self.redeal_btn = Button(
            text='Redeal',
            size_hint=(None, None),
            size=(button_width, button_height),
            pos=(button_x, Window.height * 0.5)
        )
        self.redeal_btn.bind(on_press=self.init_game)
        self.add_widget(self.redeal_btn)

        self.autoplay_btn = Button(
            text='Autoplay',
            size_hint=(None, None),
            size=(button_width, button_height),
            pos=(button_x, Window.height * 0.3)
        )
        self.autoplay_btn.bind(on_press=self.toggle_autoplay)
        self.add_widget(self.autoplay_btn)

        # Update cards label position and ensure it's removed/readded
        self.cards_label = Label(
            text=f'Cards: {self.total_cards}',
            size_hint=(None, None),
            size=(button_width, button_height),
            pos=(button_x, Window.height * 0.1)
        )
        self.add_widget(self.cards_label)

    def load_cards(self):
        suits = {'h': 'hearts', 'd': 'diamonds', 'c': 'clubs', 's': 'spades'}
        ranks = {
            '2': '2', '3': '3', '4': '4', '5': '5', '6': '6', '7': '7', '8': '8', 
            '9': '9', '10': '10', 'j': 'jack', 'q': 'queen', 'k': 'king', 'a': 'ace'
        }
        
        for suit_short, suit_long in suits.items():
            for rank_short, rank_long in ranks.items():
                filename = f"{rank_long}_of_{suit_long}.png"
                path = os.path.join("resources", "cards", "pngfree", filename)
                self.card_images[f"{rank_short}_of_{suit_short}"] = path
                
        self.card_back = os.path.join("resources", "cards", "pngfree", "Card-Back.jpg")

    def init_game(self, *args):
        self.game_start_time = time()
        suits = ['h', 'd', 'c', 's']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'j', 'q', 'k', 'a']
        self.deck = [f"{rank}_of_{suit}" for suit in suits for rank in ranks]
        random.shuffle(self.deck)
        self.dealt_cards = []
        self.total_cards = 52
        self.cards_in_deck = 52
        self.autoplay_active = False
        self.update_card_positions()

    def update_card_positions(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0, 0.5, 0)
            Rectangle(pos=self.pos, size=self.size)
            
        # Calculate card size based on orientation
        if self.is_portrait:
            card_width = Window.width * 0.125
            deck_x = Window.width * 0.025
            deck_y = Window.height * 0.033
            cards_y = Window.height * 0.33
        else:
            card_width = Window.width * 0.1  # Smaller in landscape
            deck_x = Window.width * 0.1  # Move deck right to account for buttons
            deck_y = Window.height * 0.1
            cards_y = Window.height * 0.5  # Center cards vertically
            
        card_height = card_width * 1.4
        
        # Remove existing cards
        for child in self.children[:]:
            if isinstance(child, Card):
                self.remove_widget(child)
                
        # Draw deck
        if self.cards_in_deck > 0:
            deck_card = Card(
                source=self.card_back,
                pos=(deck_x, deck_y),
                size=(card_width, card_height)
            )
            self.add_widget(deck_card)
            
        # Draw dealt cards
        display_cards = self.get_display_cards()
        card_spacing = card_width * 1.1
        
        for i, card in enumerate(display_cards):
            x_pos = deck_x + card_spacing + (i * card_spacing)
            card_widget = Card(
                source=self.card_images[card],
                pos=(x_pos, cards_y),
                size=(card_width, card_height)
            )
            self.add_widget(card_widget)

        self.cards_label.text = f'Cards: {self.total_cards}'
        
        if self.check_game_over():
            if self.autoplay_active:
                self.toggle_autoplay()  # Stop autoplay
            # Could add game over notification here

    def get_display_cards(self):
        return self.dealt_cards[-5:] if len(self.dealt_cards) > 5 else self.dealt_cards

    def check_cards(self, *args):
        if len(self.dealt_cards) >= 4:
            current_card = self.dealt_cards[-1]
            fourth_card = self.dealt_cards[-4]
            
            current_rank, current_suit = current_card.split('_of_')
            fourth_rank, fourth_suit = fourth_card.split('_of_')
            
            if current_suit == fourth_suit:
                del self.dealt_cards[-3:-1]
                self.total_cards -= 2
                print("Suit match! Removed middle two cards.")
            elif current_rank == fourth_rank:
                del self.dealt_cards[-4:]
                self.total_cards -= 4
                print("Rank match! Removed all four cards.")
            else:
                print("No match found.")
        
        self.update_card_positions()
        if self.cards_in_deck == 0:  # Add this check
            self.check_game_over()

    def toggle_autoplay(self, *args):
        self.autoplay_active = not self.autoplay_active
        if self.autoplay_active:
            Clock.schedule_interval(self.autoplay_step, 0.5)
        else:
            Clock.unschedule(self.autoplay_step)

    def autoplay_step(self, dt):
        if self.cards_in_deck > 0:
            dealt_card = self.deck.pop()
            self.dealt_cards.append(dealt_card)
            self.cards_in_deck -= 1
            self.check_cards()
            self.update_card_positions()
            return True
        else:
            print("No more cards in the deck.")
            Clock.unschedule(self.autoplay_step)  # Stop the autoplay clock
            self.game_over()  # Trigger game over while autoplay is still true
            return False

    def on_touch_down(self, touch):
        if super().on_touch_down(touch):
            return True
            
        # Adjust deck click area based on orientation
        if self.is_portrait:
            deck_x = Window.width * 0.025
            deck_y = Window.height * 0.033
            card_width = Window.width * 0.125
        else:
            deck_x = Window.width * 0.1
            deck_y = Window.height * 0.1
            card_width = Window.width * 0.1
            
        card_height = card_width * 1.4
        
        # Check if deck was clicked
        if (deck_x <= touch.pos[0] <= deck_x + card_width and 
            deck_y <= touch.pos[1] <= deck_y + card_height):
            if self.cards_in_deck > 0:
                dealt_card = self.deck.pop()
                self.dealt_cards.append(dealt_card)
                self.cards_in_deck -= 1
                self.update_card_positions()
                if self.cards_in_deck == 0:  # If this was the last card
                    self.game_over()  # Directly trigger game over
                return True
        return False

    def check_game_over(self):
        if self.cards_in_deck == 0:
            # Do one final check of the cards
            if len(self.dealt_cards) >= 4:
                current_card = self.dealt_cards[-1]
                fourth_card = self.dealt_cards[-4]
                
                current_rank, current_suit = current_card.split('_of_')
                fourth_rank, fourth_suit = fourth_card.split('_of_')
                
                if current_suit == fourth_suit or current_rank == fourth_rank:
                    # There's still a valid move
                    self.check_cards()  # Perform the move
                    return False

                # Check for any other possible matches
                for i in range(len(self.dealt_cards)-3):
                    current_card = self.dealt_cards[-1]
                    fourth_card = self.dealt_cards[i]
                    
                    current_rank, current_suit = current_card.split('_of_')
                    fourth_rank, fourth_suit = fourth_card.split('_of_')
                    
                    if current_suit == fourth_suit or current_rank == fourth_rank:
                        return False  # Still have possible matches
            
            print("Triggering game over sequence")  # Debug print
            self.game_over()  # This should trigger game over
            return True
        return False

    def game_over(self):
        # Debug prints
        print("\n=== Game Over Debug ===")
        print(f"Game Start Time: {self.game_start_time}")
        print(f"Current Time: {time()}")
        print(f"Total Cards: {self.total_cards}")
        print(f"Autoplay Active: {self.autoplay_active}")
        
        # Save the autoplay state before turning it off
        was_autoplay = self.autoplay_active
        
        # Stop autoplay if active
        if self.autoplay_active:
            self.toggle_autoplay()

        # Calculate duration and status
        duration = int(time() - self.game_start_time)
        status = "won" if self.total_cards == 0 else "completed"
        
        # Debug prints
        print(f"Duration: {duration} seconds")
        print(f"Status: {status}")
        print(f"Was Autoplay: {was_autoplay}")
        
        # Save game result
        try:
            self.db.save_game_result(
                is_autoplay=was_autoplay,  # Use the saved state
                cards_remaining=self.total_cards,
                duration_seconds=duration,
                status=status
            )
            print("Game result saved successfully")
        except Exception as e:
            print(f"Error saving game result: {e}")

        # Show game over popup
        message = (
            f"Game Over!\n\n"
            f"{'🏆 Perfect Game! 🏆' if self.total_cards == 0 else ''}\n"
            f"Cards Remaining: {self.total_cards}\n"
            f"Time Played: {duration//60}m {duration%60}s\n"
            f"Mode: {'Computer' if was_autoplay else 'Human'}"  # Use the saved state
        )
        
        popup = Popup(
            title='Game Over',
            content=Label(text=message),
            size_hint=(0.8, 0.5)
        )
        popup.open()

    def show_stats(self, instance):
        stats = self.db.get_stats()
        popup_text = "Game Statistics:\n\n"
        
        for row in stats:
            game_type = "Auto-play" if row[0] else "Manual"
            games_played = row[1]
            avg_cards = round(row[2], 1) if row[2] is not None else 0
            best_result = row[3] if row[3] is not None else 0
            wins = row[4]
            
            popup_text += f"{game_type} Games:\n"
            popup_text += f"Games Played: {games_played}\n"
            popup_text += f"Average Cards Left: {avg_cards}\n"
            popup_text += f"Best Result: {best_result} cards\n"
            popup_text += f"Total Wins: {wins}\n\n"
        
        popup = Popup(
            title='Statistics',
            content=Label(text=popup_text),
            size_hint=(0.8, 0.8)
        )
        popup.open()

class CardApp(App):
    def build(self):
        return CardGame()

if __name__ == '__main__':
    CardApp().run()
