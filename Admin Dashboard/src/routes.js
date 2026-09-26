import Login from 'views/Login.jsx'
import Category from 'views/Category.jsx'
import Food from './views/Food'
import Orders from './views/Orders'
import Configuration from './views/Configuration'
import Users from './views/Users'
import Ratings from './views/Ratings'
import ResetPassword from './views/ForgotPassword'
import Options from './views/Options'
import Addons from './views/Addons'
import Coupons from './views/Coupons'
import Dashboard from './views/Dashboard'
import Notifications from './views/Notifications'
import Staff from './views/Staff'
import Restaurants from './views/Restaurants'

const DIRECTOR = ['director', 'admin']
const ALL = ['director', 'admin', 'staff']
// The platform owner is not tied to a restaurant, so tenant management is the
// only screen their role can use — and the only one that works for them.
const SUPERADMIN = ['superadmin']

var routes = [
  {
    path: '/restaurants',
    name: 'Restaurants',
    icon: 'ni ni-shop text-orange',
    component: Restaurants,
    layout: '/admin',
    appearInSidebar: true,
    roles: SUPERADMIN
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    icon: 'ni ni-tv-2 text-orange',
    component: Dashboard,
    layout: '/admin',
    appearInSidebar: true,
    roles: ALL
  },
  {
    path: '/category',
    name: 'Category',
    icon: 'ni ni-chart-pie-35 text-orange',
    component: Category,
    layout: '/admin',
    appearInSidebar: true,
    roles: DIRECTOR
  },
  {
    path: '/food',
    name: 'Food',
    icon: 'ni ni-tie-bow text-orange',
    component: Food,
    layout: '/admin',
    appearInSidebar: true,
    roles: DIRECTOR
  },
  {
    path: '/orders',
    name: 'Orders',
    icon: 'ni ni-basket text-orange',
    component: Orders,
    layout: '/admin',
    appearInSidebar: true,
    roles: ALL
  },
  {
    path: '/users',
    name: 'Users',
    icon: 'ni ni-single-02 text-orange',
    component: Users,
    layout: '/admin',
    appearInSidebar: true,
    roles: DIRECTOR
  },
  {
    path: '/staff',
    name: 'Staff',
    icon: 'ni ni-badge text-orange',
    component: Staff,
    layout: '/admin',
    appearInSidebar: true,
    roles: DIRECTOR
  },
  {
    path: '/ratings',
    name: 'Ratings',
    icon: 'fas fa-star text-orange',
    component: Ratings,
    layout: '/admin',
    appearInSidebar: true,
    roles: DIRECTOR
  },
  {
    path: '/configuration',
    name: 'Configuration',
    icon: 'ni ni-settings text-orange',
    component: Configuration,
    layout: '/admin',
    appearInSidebar: true,
    roles: DIRECTOR
  },
  {
    path: '/option',
    name: 'Option',
    icon: 'ni ni-palette text-orange',
    component: Options,
    layout: '/admin',
    appearInSidebar: true,
    roles: DIRECTOR
  },
  {
    path: '/addons',
    name: 'Addons',
    icon: 'ni ni-collection text-orange',
    component: Addons,
    layout: '/admin',
    appearInSidebar: true,
    roles: DIRECTOR
  },
  {
    path: '/coupons',
    name: 'Coupons',
    icon: 'ni ni-single-copy-04 text-orange',
    component: Coupons,
    layout: '/admin',
    appearInSidebar: true,
    roles: DIRECTOR
  },
  {
    path: '/notifications',
    name: 'Notifications',
    icon: 'ni ni-bell-55 text-orange',
    component: Notifications,
    layout: '/admin',
    appearInSidebar: true,
    roles: DIRECTOR
  },
  {
    path: '/login',
    name: 'Login',
    icon: 'ni ni-key-25 text-info',
    component: Login,
    layout: '/auth',
    appearInSidebar: false,
    roles: ALL
  },
  {
    path: '/reset',
    name: 'ResetPassword',
    icon: 'ni ni-key-25 text-info',
    component: ResetPassword,
    layout: '/auth',
    appearInSidebar: false,
    roles: ALL
  }
]
export default routes
