## Конфігурація підключення до бази даних

Для налаштування з'єднання з базою даних, необхідно створити файл `.env` у корені проекту та визначити в ньому параметри підключення. Цей файл використовується для зберігання конфіденційної інформації. Нижче наведено приклад змінних, які вам потрібно вказати:

- `DEFAULT_HOST`: Хост вашої бази даних.
  - **Приклад**: `localhost` для локального сервера.

- `DEFAULT_PORT`: Порт, на якому працює ваша база даних.
  - **Приклад**: `5432` для PostgreSQL.

- `DEFAULT_DB`: Назва вашої бази даних.
  - **Приклад**: `taekwondo` для системи управління змаганнями з тхеквондо.

- `DEFAULT_USER`: Ім'я користувача для доступу до бази даних.
  - **Приклад**: `postgres` для PostgreSQL.

- `DEFAULT_PASSWORD`: Пароль для доступу до бази даних.
  - **Приклад**: `yourpassword`.

### Приклад файлу `.env`:

```plaintext
DEFAULT_HOST="localhost"
DEFAULT_PORT=5432
DEFAULT_DB="taekwondo"
DEFAULT_USER="postgres"
DEFAULT_PASSWORD="yourpassword"
