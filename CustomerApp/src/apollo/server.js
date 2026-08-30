export const login = `
mutation Login($facebookId:String,$email:String,$password:String,$type:String!,$appleId:String,$name:String,$notificationToken:String){
    login(facebookId:$facebookId,email:$email,password:$password,type:$type,appleId:$appleId,name:$name,notificationToken:$notificationToken){
     userId
     token
     is_active
     tokenExpiration
     name
     email
     phone
   }
}
`;

export const categories = `
{
  categories{
  _id
  title
  description
  img_menu
  }
}`;

export const foods = `
query FoodByCategory($category:String!,$onSale:Boolean,$inStock:Boolean,$min:Float,$max:Float,$search:String){
    foodByCategory(category:$category,onSale:$onSale,inStock:$inStock,min:$min,max:$max,search:$search){
      _id
      title
      description
      variations{
        _id
        title
        price
        discounted
        addons{
          _id
          title
          description
          quantity_minimum
          quantity_maximum
          options{
            _id
            title
            description
            price
          }
        }
      }
      category{_id}
      img_url
      stock
    }
  }`;

export const createUser = `
  mutation CreateUser($facebookId:String,$phone:String,$email:String,$password:String,$name:String,$notificationToken:String,$appleId:String){
      createUser(userInput:{
          facebookId:$facebookId,
          phone:$phone,
          email:$email,
          password:$password,
          name:$name,
          notificationToken:$notificationToken,
          appleId:$appleId
      }){
          userId
          token
          tokenExpiration
          name
          email
          phone
          notificationToken
      }
    }`;

export const updateUser = `
    mutation UpdateUser($name:String!,$phone:String!,$is_active:Boolean!){
        updateUser(updateUserInput:{name:$name,phone:$phone,is_active:$is_active}){
          _id
          name
          phone
          is_active
        }
      }`;

export const updateNotificationStatus = `
    mutation UpdateNotificationStatus($offerNotification:Boolean!,$orderNotification:Boolean!){
      updateNotificationStatus(offerNotification:$offerNotification,orderNotification:$orderNotification){
        _id
        notificationToken
        is_order_notification
        is_offer_notification
      }
    }`;
export const profile = `
        query{
          profile{
            _id
            name
            phone
            email
            is_active
            
            notificationToken
            is_order_notification
            is_offer_notification
            addresses{
              _id
              label
              delivery_address
              details
              longitude
              latitude
              selected
            }
          }
        }`;

export const order = `query Order($id:String!){
  order(id:$id){
    _id
    order_id
    user{
      _id
      phone
    }
    items{
      _id
      food{
        _id
        title
        category{
          _id
        }
        description
        img_url
        
      }
      variation{
        _id
        title
        price
      }
      addons{
        _id
        title
        description
        quantity_minimum
        quantity_maximum
        options{
          _id
          title
          description
          price
        }
      }
      quantity
    }
    payment_status
    payment_method
    order_amount
    paid_amount
    order_status
    status_queue{
      pending
      preparing
      ready
      completed
      cancelled
    }
    createdAt
    review{
      _id
      rating
      description
    }
  }
}
`;

export const myOrders = `query Orders($offset:Int){
  orders(offset:$offset){
    _id
    order_id
    user{
      _id
      phone
    }
    
    items{
      _id
      food{
        _id
        title
        category{
          _id
        }
        description
        img_url
      }
      variation{
        _id
        title
        price
      }
      addons{
        _id
        title
        description
        quantity_minimum
        quantity_maximum
        options{
          _id
          title
          description
          price
        }
      }
      quantity
    }
    payment_status
    payment_method
    order_amount
    paid_amount
    order_status
    status_queue{
      pending
      preparing
      ready
      completed
      cancelled
    }
    createdAt
    review{
      _id
      rating
      description
    }
  }
}
`;

//
// can we get userId from request instead??
// needs research
//

export const orderStatusChanged = `subscription OrderStatusChanged($userId:String!){
  orderStatusChanged(userId:$userId)
  {
    userId
    origin
    order{
    _id
    order_id
    user{
      _id
      phone
    }
    
    items{
      _id
      food{
        _id
        title
        category{
          _id
        }
        description
        img_url
      }
      variation{
        _id
        title
        price
      }
      addons{
        _id
        title
        description
        quantity_minimum
        quantity_maximum
        options{
          _id
          title
          description
          price
        }
      }
      quantity
    }
    payment_status
    payment_method
    order_amount
    paid_amount
    order_status
    status_queue{
      pending
      preparing
      ready
      completed
      cancelled
    }
    createdAt
    review{
      _id
      rating
      description
    }
  }
  }
}
`;

//
// status queue??
// can we use address id instead of address object, then get the address on backend??
//
export const placeOrder = `
mutation PlaceOrder($orderInput:[OrderInput!]!,$paymentMethod:String!,$couponCode:String){
  placeOrder(orderInput: $orderInput,paymentMethod:$paymentMethod,couponCode:$couponCode) {
    _id
    order_id
    items{
      _id
      food{
        _id
        title
        category{
          _id
        }
        description
        img_url
      }
      variation{
        _id
        title
        price
      }
      addons{
        _id
        title
        description
        quantity_minimum
        quantity_maximum
        options{
          _id
          title
          description
          price
        }
      }
      quantity
    }
    user {
      _id
      phone
      email
    }
    payment_status
    payment_method
    paid_amount
    order_amount
    order_status
    status_queue{
      pending
      preparing
      ready
      completed
      cancelled
    }
    createdAt
    review{
      _id
      rating
      description
    }
  }
}`;

export const reviewOrder = `mutation ReviewOrder(
  $orderId:String!,
  $rating:Int!,
  $description:String
){
  reviewOrder(reviewInput:{
    orderId:$orderId,
    rating:$rating,
    description:$description
  }){
    _id
    order_id
    review{
      _id
      rating
      description
    }
    createdAt
    updatedAt
    is_active
  }
}`;


export const pushToken = `mutation PushToken($token:String!){
  pushToken(token:$token){
    _id
    notificationToken
  }
}`;

export const getConfiguration = `query Configuration{
  configuration{
    _id
    currency
    currency_symbol
  }
}`;

export const foodByIds = `query FoodByIds($ids:[String!]!){
  foodByIds(ids: $ids) {
    _id
    title
    description
    img_url
    stock
    category {
      _id
    }
    variations {
      _id
      title
      price
      discounted
      addons {
        _id
        title
        description
        quantity_minimum
        quantity_maximum
        options {
          _id
          title
          description
          price
        }
      }
    }
  }
}`;

export const getCoupon = `mutation Coupon($coupon:String!){
  coupon(coupon:$coupon){
    _id
    code
    discount
    enabled
  }
}`;

export const deleteAddress = `mutation DeleteAddress($id:ID!){
  deleteAddress(id:$id){
    _id
    addresses{
      _id
      label
      delivery_address
      details
      longitude
      latitude
      selected
    }
  }
}`;

export const createAddress = `mutation CreateAddress($addressInput:AddressInput!){
  createAddress(addressInput:$addressInput){
    _id
    addresses{
      _id
      label
      delivery_address
      details
      longitude
      latitude
      selected
    }
  }
}`;

export const editAddress = `mutation EditAddress($addressInput:AddressInput!){
  editAddress(addressInput:$addressInput){
    _id
    label
    delivery_address
    details
    longitude
    latitude
  }
}`;

export const changePassword = `mutation ChangePassword($oldPassword:String!,$newPassword:String!){
  changePassword(oldPassword:$oldPassword,newPassword:$newPassword)
}`;

export const forgotPassword = `mutation ForgotPassword($email:String!){
  forgotPassword(email:$email){
    result
  }
}`;

export const selectAddress = `mutation SelectAddress($id:String!){
  selectAddress(id:$id){
    _id
    addresses{
      _id
      label
      delivery_address
      details
      longitude
      latitude
      selected
    }
  }
}`;
