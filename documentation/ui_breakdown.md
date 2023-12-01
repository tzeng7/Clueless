# UI Framework

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

## View
- describe what a View is composed of, functionality (managing lists of elements, 
abstracting away pygame vs. pygame_gui elements and differences in adding/removing those different elements)
- dispatches I/O events back to corresponding Elements so that Elements can call their delegate methods

## Elements
- Class hierarchy for Element (pygame) and ManagedElement (pygame_gui)
- any wrapped element + a Rectangle
- Stacks + resizing


## Example using TitleView


## Example using ActionView