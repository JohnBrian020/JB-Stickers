import { Routes, Route, Navigate } from 'react-router-dom'

import MainLayout from '../components/layout/MainLayout'
import AdminLayout from '../components/layout/AdminLayout'
import AdminRoute from './AdminRoute'

import Home from '../pages/Home'
import Shop from '../pages/Shop'
import About from '../pages/About'
import Contact from '../pages/Contact'
import Cart from '../pages/Cart'
import Checkout from '../pages/Checkout'
import OrderConfirmation from '../pages/OrderConfirmation'
import ProductDetails from '../pages/ProductDetails'
import NotFound from '../pages/NotFound'
import ManageProducts from '../pages/admin/ManageProducts'
import ManageOrders from '../pages/admin/ManageOrders'
import OrderDetails from '../pages/admin/OrderDetails'

import AdminLogin from '../pages/admin/AdminLogin'
import Dashboard from '../pages/admin/Dashboard'
import AccountSettings from '../pages/admin/AccountSettings'

function AppRoutes() {
  return (
    <Routes>
      {/* Admin login */}
      <Route path="/admin/login" element={<AdminLogin />} />

      {/* Protected admin pages */}
      <Route element={<AdminRoute />}>
        <Route path="/admin" element={<AdminLayout />}>
            <Route index element={<Navigate to="dashboard" replace />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="orders" element={<ManageOrders />} />
            <Route path="orders/:orderId" element={<OrderDetails />} />
            <Route path="products" element={<ManageProducts />} />
            <Route path="account" element={<AccountSettings />} />
        </Route>
      </Route>

      {/* Customer storefront */}
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
      </Route>

      <Route path="*" element={<NotFound />} />
    </Routes>
  )
}

export default AppRoutes