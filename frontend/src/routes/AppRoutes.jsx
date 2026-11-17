
import { Routes, Route, Navigate } from 'react-router-dom'
import MainLayout from '../components/layout/MainLayout'
import Home from '../pages/Home'
import Shop from '../pages/Shop'
import About from '../pages/About'
import Contact from '../pages/Contact'
import Cart from '../pages/Cart'
import Checkout from '../pages/Checkout'
import OrderConfirmation from '../pages/OrderConfirmation'
import NotFound from '../pages/NotFound'
import ProductDetails from '../pages/ProductDetails'

function AppRoutes() {
  return (
    <Routes>
      <Route element={<MainLayout />}>
        <Route path="/" element={<Home />} />
        <Route path="/shop" element={<Shop />} />
        <Route path="/shop/:productId" element={<ProductDetails />} />
        <Route path="/about" element={<About />} />
        <Route path="/contact" element={<Contact />} />
        <Route path="/cart" element={<Cart />} />
        <Route path="/checkout" element={<Checkout />} />
        <Route
          path="/order-confirmation/:trackingToken"
          element={<OrderConfirmation />}
        />
        <Route path="/home" element={<Navigate to="/" replace />} />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  )
}

export default AppRoutes

