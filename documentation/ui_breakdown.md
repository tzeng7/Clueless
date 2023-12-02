# Drawing UI

## `pygame` & `pygame_gui`

The `pygame` library gives us the ability to draw on top of an app window and manage an event loop for us to 
receive and respond to I/O events in that window.

The most important class in pygame is `pygame.Surface`. `pygame.display`, which is the entire `pygame` window, is a pygame
Surface. Pygame gives us utilities to draw text and shapes onto this window.

However, this functionality is pretty basic. For example, it does not support a text-input field out of the box. If we 
wanted to implement a text-input field in `pygame` alone, we would have to draw a rectangle, implement a cursor, and respond
to each key event one by one. To simplify, we imported `pygame_gui`, which provides more complex elements (like text input and buttons).

`pygame_gui` has its own way of managing elements and drawing them to the screen. For vanilla pygame, we usually
use `pygame.draw` and `pygame.Surface.blit` to draw directly onto the Surface. `pygame_gui` uses a UIManager to 
manage all `pygame_gui.UIElement`s, and the UIManager draws them all onto the Surface.

## UI Framework

To manage `pygame` and `pygame_gui` elements, we introduce two types of classes: Views and Elements. 

A View is composed of multiple elements and takes up the entire screen. The view is responsible for drawing those
elements onto its `pygame.Surface` screen, adding and removing elements, and dispatching pygame events to its elements.


## Elements

- Stacks + resizing
- cleanup for stacks


## Example using TitleView


## Example using ActionView