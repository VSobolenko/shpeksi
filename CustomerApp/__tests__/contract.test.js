import * as operations from '../src/apollo/server'

const operationNames = [
  'login',
  'categories',
  'foods',
  'createUser',
  'updateUser',
  'updateNotificationStatus',
  'profile',
  'order',
  'myOrders',
  'orderStatusChanged',
  'placeOrder',
  'reviewOrder',
  'pushToken',
  'getConfiguration',
  'foodByIds',
  'getCoupon',
  'deleteAddress',
  'createAddress',
  'editAddress',
  'changePassword',
  'forgotPassword',
  'selectAddress'
]

describe('GraphQL contract (src/apollo/server.js)', () => {
  it('exports every fixed operation', () => {
    operationNames.forEach((name) => {
      expect(operations[name]).toBeDefined()
      expect(typeof operations[name]).toBe('string')
      expect(operations[name].length).toBeGreaterThan(0)
    })
  })

  it('keeps snake_case field names intact', () => {
    const all = operationNames.map((name) => operations[name]).join('\n')
    const fields = ['order_amount', 'payment_status', 'payment_method', 'delivery_address', 'order_id', 'is_order_notification', 'is_offer_notification']
    fields.forEach((field) => {
      expect(all).toContain(field)
    })
  })

  it('keeps operation names intact', () => {
    expect(operations.login).toContain('mutation Login')
    expect(operations.foods).toContain('FoodByCategory')
    expect(operations.myOrders).toContain('Orders')
    expect(operations.orderStatusChanged).toContain('OrderStatusChanged')
    expect(operations.placeOrder).toContain('PlaceOrder')
  })
})
