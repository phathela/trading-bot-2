import os
import logging
from datetime import datetime
from pybit.unified_trading import HTTP
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BybitTrader:
    def __init__(self, api_key, api_secret, testnet=True):
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet

        self.session = HTTP(
            testnet=testnet,
            api_key=api_key,
            api_secret=api_secret
        )

        self.leverage = 10
        self.balance_usage = 0.90
        self.stop_loss_percent = 0.24
        self.stop_loss_price_percent = 0.024

        self.position = None
        self.entry_price = None

    def get_wallet_balance(self, coin="USDT"):
        try:
            response = self.session.get_wallet_balance(accountType="UNIFIED", coin=coin)
            if response['retCode'] == 0:
                balance = float(response['result']['list'][0]['coin'][0]['walletBalance'])
                logger.info(f"Wallet balance: {balance} {coin}")
                return balance
            else:
                logger.error(f"Error fetching balance: {response['retMsg']}")
                return 0
        except Exception as e:
            logger.error(f"Error getting wallet balance: {str(e)}")
            return 0

    def get_current_price(self, symbol="BTCUSDT"):
        try:
            response = self.session.get_tickers(category="linear", symbol=symbol)
            if response['retCode'] == 0:
                price = float(response['result']['list'][0]['lastPrice'])
                logger.info(f"Current price for {symbol}: {price}")
                return price
            else:
                logger.error(f"Error fetching price: {response['retMsg']}")
                return None
        except Exception as e:
            logger.error(f"Error getting current price: {str(e)}")
            return None

    def calculate_position_size(self, balance, symbol="BTCUSDT"):
        """Calculate position size based on 90% balance usage with leverage"""
        try:
            current_price = self.get_current_price(symbol)
            if not current_price:
                return 0

            usable_balance = balance * self.balance_usage
            position_value = usable_balance * self.leverage
            position_size = position_value / current_price

            logger.info(f"Position size calculation:")
            logger.info(f"  Balance: {balance}, Usable (90%): {usable_balance}")
            logger.info(f"  Position value with {self.leverage}x leverage: {position_value}")
            logger.info(f"  Position size in {symbol}: {position_size}")

            return position_size
        except Exception as e:
            logger.error(f"Error calculating position size: {str(e)}")
            return 0

    def set_leverage(self, symbol="BTCUSDT", leverage=10):
        try:
            response = self.session.set_leverage(
                category="linear",
                symbol=symbol,
                buyLeverage=str(leverage),
                sellLeverage=str(leverage)
            )
            if response['retCode'] == 0:
                logger.info(f"Leverage set to {leverage}x for {symbol}")
                return True
            else:
                logger.error(f"Error setting leverage: {response['retMsg']}")
                return False
        except Exception as e:
            logger.error(f"Error setting leverage: {str(e)}")
            return False

    def open_position(self, symbol="BTCUSDT", side="Buy", qty=None):
        """Open a new position"""
        try:
            if qty is None:
                balance = self.get_wallet_balance()
                qty = self.calculate_position_size(balance, symbol)

            if qty <= 0:
                logger.error("Invalid position size")
                return False

            qty = round(qty, 4)
            logger.info(f"Opening {side} position for {qty} {symbol}")

            response = self.session.place_order(
                category="linear",
                symbol=symbol,
                side=side,
                orderType="Market",
                qty=str(qty),
                leverage=str(self.leverage)
            )

            if response['retCode'] == 0:
                order_id = response['result']['orderId']
                logger.info(f"Order placed successfully. Order ID: {order_id}")

                self.position = {
                    'symbol': symbol,
                    'side': side,
                    'qty': qty,
                    'order_id': order_id,
                    'timestamp': datetime.now().isoformat()
                }

                time.sleep(1)
                self.entry_price = self.get_current_price(symbol)
                self.position['entry_price'] = self.entry_price

                return True
            else:
                logger.error(f"Error placing order: {response['retMsg']}")
                return False

        except Exception as e:
            logger.error(f"Error opening position: {str(e)}")
            return False

    def close_position(self, symbol="BTCUSDT"):
        """Close the current position"""
        try:
            if not self.position:
                logger.warning("No position to close")
                return False

            opposite_side = "Sell" if self.position['side'] == "Buy" else "Buy"
            logger.info(f"Closing position with {opposite_side} order")

            response = self.session.place_order(
                category="linear",
                symbol=symbol,
                side=opposite_side,
                orderType="Market",
                qty=str(self.position['qty']),
                reduceOnly=True
            )

            if response['retCode'] == 0:
                order_id = response['result']['orderId']
                logger.info(f"Close order placed successfully. Order ID: {order_id}")

                exit_price = self.get_current_price(symbol)
                pnl = self.calculate_pnl(
                    entry_price=self.position['entry_price'],
                    exit_price=exit_price,
                    qty=self.position['qty'],
                    side=self.position['side']
                )

                logger.info(f"Position closed. P&L: {pnl}")
                self.position = None
                self.entry_price = None

                return True
            else:
                logger.error(f"Error closing position: {response['retMsg']}")
                return False

        except Exception as e:
            logger.error(f"Error closing position: {str(e)}")
            return False

    def check_stop_loss(self, symbol="BTCUSDT"):
        """Check if stop loss should be triggered"""
        if not self.position or not self.entry_price:
            return False

        current_price = self.get_current_price(symbol)
        if not current_price:
            return False

        price_change_percent = abs(current_price - self.entry_price) / self.entry_price

        if price_change_percent >= self.stop_loss_price_percent:
            logger.warning(f"Stop loss triggered by price movement: {price_change_percent:.4f}")
            return True

        if price_change_percent >= self.stop_loss_percent:
            logger.warning(f"Stop loss triggered by 24% loss: {price_change_percent:.4f}")
            return True

        return False

    def calculate_pnl(self, entry_price, exit_price, qty, side="Buy"):
        """Calculate P&L for a position"""
        if side == "Buy":
            pnl = (exit_price - entry_price) * qty
        else:
            pnl = (entry_price - exit_price) * qty

        return round(pnl, 2)

    def get_position_status(self, symbol="BTCUSDT"):
        """Get current position information"""
        try:
            response = self.session.get_positions(
                category="linear",
                symbol=symbol
            )

            if response['retCode'] == 0:
                positions = response['result']['list']
                if positions:
                    return positions
                else:
                    logger.info("No active positions")
                    return None
            else:
                logger.error(f"Error getting position: {response['retMsg']}")
                return None

        except Exception as e:
            logger.error(f"Error getting position status: {str(e)}")
            return None
