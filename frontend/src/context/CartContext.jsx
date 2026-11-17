
import { createContext, useContext, useEffect, useState } from 'react'

const CartContext = createContext(null)

function getSavedCart() {
  try {
    const savedCart = localStorage.getItem('xoxo-cart')
    return savedCart ? JSON.parse(savedCart) : []
  } catch {
    return []
  }
}

export function CartProvider({ children }) {
  const [cartItems, setCartItems] = useState(getSavedCart)

  useEffect(() => {
    localStorage.setItem('xoxo-cart', JSON.stringify(cartItems))
  }, [cartItems])

  
function addToCart(product, quantity = 1) {
  if (!product || product.stock <= 0) return false

  const existingItem = cartItems.find(
    (item) => item.id === product.id
  )

  if (existingItem && existingItem.quantity >= product.stock) {
    return false
  }

  if (existingItem) {
    setCartItems((currentItems) =>
      currentItems.map((item) =>
        item.id === product.id
          ? {
              ...item,
              quantity: Math.min(
                item.quantity + quantity,
                product.stock
              ),
              stock: product.stock,
            }
          : item
      )
    )
  } else {
    setCartItems((currentItems) => [
      ...currentItems,
      {
        id: product.id,
        name: product.name,
        price: Number(product.price),
        image_url: product.image_url,
        stock: product.stock,
        quantity: Math.min(quantity, product.stock),
      },
    ])
  }

  return true
}


  function updateQuantity(productId, quantity) {
    setCartItems((currentItems) =>
      currentItems.map((item) =>
        item.id === productId
          ? {
              ...item,
              quantity: Math.max(
                1,
                Math.min(Number(quantity) || 1, item.stock)
              ),
            }
          : item
      )
    )
  }

  function removeFromCart(productId) {
    setCartItems((currentItems) =>
      currentItems.filter((item) => item.id !== productId)
    )
  }

  function clearCart() {
    setCartItems([])
  }

  const cartCount = cartItems.reduce(
    (total, item) => total + item.quantity,
    0
  )

  const cartTotal = cartItems.reduce(
    (total, item) => total + item.price * item.quantity,
    0
  )

  return (
    <CartContext.Provider
      value={{
        cartItems,
        cartCount,
        cartTotal,
        addToCart,
        updateQuantity,
        removeFromCart,
        clearCart,
      }}
    >
      {children}
    </CartContext.Provider>
  )
}
// eslint-disable-next-line react-refresh/only-export-components
export function useCart() {
  const context = useContext(CartContext)

  if (!context) {
    throw new Error('useCart must be used inside CartProvider')
  }

  return context
}

