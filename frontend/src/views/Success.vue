<template>
  <h1>Payment success</h1>
</template>

<script>
export default {
  data() {
    return {
      user: null,
    };
  },
  async mounted() {
    const storedUser = localStorage.getItem("user_id");
    const transaction = sessionStorage.getItem("transaction");
    const transactiondata = JSON.parse(transaction);
    console.log(transactiondata.OrderID);
    const vendorCuisine = sessionStorage.getItem("cuisine");
    const vendorName = sessionStorage.getItem("vendorname");
    const savedCart = JSON.parse(sessionStorage.getItem("cart") || "[]");
    console.log("Saved Cart:", savedCart);

    const mappedCart = savedCart.map((item) => {
      return {
        Id: item.ItemID,
        VendorID: item.VendorID,
        VendorName: vendorName,
        Cuisine: vendorCuisine,
        ImageURL: item.ImageURL,
        OrderId: transactiondata.OrderID,
      };
    });

    this.requestBody = {
      UserOrdersAPI: {
        UserID: storedUser,
        OrderID: transactiondata.OrderID,
        OrderDetails: mappedCart,
      },
    };
    this.orderRequestBody = {
      UserID: storedUser,
      TotalAmount: transactiondata.Amount,
      TransactionID: transactiondata.TransactionID,
    };

    const cartitems = savedCart.map((item) => {
      return {
        ItemID: item.ItemID,
        ItemName: item.ItemName,
        Quantity: 1,
        Price: item.Price,
        VendorID: item.VendorID
      };
    });

    this.orderData = {
      OrderID: transactiondata.OrderID,
      UserID: storedUser,
      TotalAmount: transactiondata.Amount,
      TransactionID: transactiondata.TransactionID,
      VendorID: savedCart.length > 0 ? savedCart[0].VendorID : null,
      VendorName: vendorName,
      Cuisine: vendorCuisine,
      ImageURL: savedCart.length > 0 ? savedCart[0].ImageURL : "",
      Items: cartitems,
    };
    console.log(this.orderData);

    this.postOrderHistory();
    this.postOrder();
  },
  methods: {
    async postOrderHistory() {
      try {
        const response = await fetch(
          "https://personal-aefq3pkb.outsystemscloud.com/OrderManagement/rest/OrderHistory/createHistory",
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify(this.requestBody),
          }
        );

        if (!response.ok) {
          throw new Error(
            `Server error: ${response.status} ${response.statusText}`
          );
        }

        const data = await response.json();
        console.log("Order history created successfully:", data);
      } catch (error) {
        console.error("Error posting order history:", error);
      }
    },
    async postOrder() {
      try {
        const response = await fetch("http://localhost:5003/orders", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(this.orderData),
        });
        if (!response.ok) {
          throw new Error(
            `Server error: ${response.status} ${response.statusText}`
          );
        }
        const data = await response.json();
        console.log("Order created successfully:", data);
      } catch (error) {
        console.error("Error creating order:", error);
      }
    },
  },
};
</script>
