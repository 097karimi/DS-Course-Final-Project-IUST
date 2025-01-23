from django.db import connections
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.timezone import now, timedelta

class StockDataView(APIView):
    def get(self, request):
        current_time = now()
        half_hour_ago = current_time - timedelta(minutes=30)

        try:
            # اتصال به QuestDB
            with connections['questdb'].cursor() as cursor:
                 # تبدیل زمان به فرمت مناسب برای QuestDB
                start_time = half_hour_ago.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
                end_time = current_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

                # اجرای کوئری برای دریافت داده‌های ۳۰ دقیقه گذشته
                query = """
                    SELECT * FROM stock_data
                    WHERE local_time >= %s AND local_time <= %s
                """
                cursor.execute(query, [start_time, end_time])
                results = cursor.fetchall()
            # تبدیل نتایج به فرمت مناسب برای پاسخ API
            data = []
            for row in results:
                data.append({
                    'stock_symbol': row[0],
                    'topic': row[1],
                    'signal': row[2],
                    'local_time': row[3],
                    'open': row[4],
                    'close': row[5],
                    'high': row[6],
                    'low': row[7],
                    'volume': row[8],
                    'SMA_5': row[9],
                    'EMA_10': row[10],
                    'delta': row[11],
                    'gain': row[12],
                    'loss': row[13],
                    'avg_gain_10': row[14],
                    'avg_loss_10': row[15],
                    'rs': row[16],
                    'RSI_10': row[17],
                })

            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)