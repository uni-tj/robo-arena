# Sprintlog 5

## Menues

_[@JulesOxe](https://github.com/uni-tj/robo-arena/commits?author=JulesOxe) (Julius Oexle)_

For our MVP, we had agreed on a simple main menu and a settings menu. You should be able to start the game and access the settings via the main menu. In the settings, you should be able to switch off the sound and change the button assignment for the controls.
Firstly, I created generic buttons and generic text fields.

Generic buttons:
- can be positioned using a relative position
- change their appearance when you move the mouse over them
- execute a function when they are clicked

Generic Textfields:
- can be positioned via a relative position
- Adjustable font size
- currently still a standard font

Multiple buttons and text fields can be managed by a menu class whose object represents a menu page. Each menu takes care of its own rendering and informs its buttons about the mouse position.

Two new functions have been developed for the settings:
- Toggle sound:
    - recognises whether the sound is currently on or off and toggles it and changes the display of the button

- Change Key Binding
    - If you click on such a button with this function, you can click on any key and this will be responsible for selected controls in future
    - The process can be cancelled with Escape
    - The key bindings are saved in a yml file and loaded when the game is started
    - even if the game is restarted, the old key bindings are still set.

A function was developed for the interface that fills a surface with a colour gradient to make the backgrounds of the menus more appealing. Customised pixel graphics were created for all buttons to show whether the mouse is on the button or not.

A current problem is that the elements of the menu scale independently, but overlap at a certain point. This would probably be difficult to solve with a dynamic grid system like in CSS, but it exceeds the amount of time that has been planned for the MVP for the menu.