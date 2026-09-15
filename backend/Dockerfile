FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
# lxml pinned and installed ahead of the rest: resolving it together with
# yfinance's loose ">=4.9.0" bound against the full requirement set makes
# pip's backtracking resolver report "no versions" even though the package
# installs cleanly on its own -- pre-pinning it sidesteps that.
RUN pip install --no-cache-dir lxml==6.1.3
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
