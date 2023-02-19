from yoomoney import Authorize

def auth():
    Authorize(
          client_id="E5C83243EDEC858A4FB609B119B3908B7FC693255792363EAF888AC48C62AB2D",
          redirect_uri="http://188.120.226.131",
          scope=[
                 "account-info",
                 "operation-history",
                 "operation-details",
                 "incoming-transfers",
                 "payment-p2p",
                 "payment-shop",
                 ]
          )