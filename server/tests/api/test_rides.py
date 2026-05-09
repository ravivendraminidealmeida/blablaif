from datetime import datetime, timedelta


def register_and_login(client, email, name="Test User"):
    client.post("/api/v1/auth/register", json={
        "name": name,
        "email": email,
        "phone": "999999999",
        "role": "Student",
        "college_id": 1,
        "password": "securepassword123"
    })
    response = client.post("/api/v1/auth/login", data={
        "username": email,
        "password": "securepassword123"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def ride_payload(**overrides):
    payload = {
        "direction": "ToCampus",
        "origin": "Centro de Votuporanga",
        "destination": "IFSP Campus Votuporanga",
        "departure_time": (datetime.now() + timedelta(days=1)).isoformat(),
        "available_seats": 2,
        "price_per_seat": "5.50",
        "allow_custom_pickup": False,
        "fixed_gathering_point": "Praca Matriz",
        "notes": "Saida pontual."
    }
    payload.update(overrides)
    return payload


def create_ride(client, headers, **overrides):
    response = client.post("/api/v1/rides", json=ride_payload(**overrides), headers=headers)
    assert response.status_code == 201, response.text
    return response.json()


def create_request(client, headers, ride_id, pickup_address="Praca Matriz"):
    return client.post(f"/api/v1/rides/{ride_id}/requests", json={
        "pickup_address": pickup_address,
        "message": "Posso ir no banco de tras."
    }, headers=headers)


def test_create_and_list_available_rides(client, setup_college):
    driver_headers = register_and_login(client, "driver@aluno.ifsp.edu.br", "Driver")
    passenger_headers = register_and_login(client, "passenger@aluno.ifsp.edu.br", "Passenger")

    ride = create_ride(client, driver_headers)
    response = client.get("/api/v1/rides", headers=passenger_headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == ride["id"]
    assert data[0]["rider_name"] == "Driver"
    assert data[0]["rider_phone"] is None
    assert data[0]["accepted_seats"] == 0


def test_driver_cannot_request_own_ride(client, setup_college):
    driver_headers = register_and_login(client, "driver@aluno.ifsp.edu.br", "Driver")
    ride = create_ride(client, driver_headers)

    response = create_request(client, driver_headers, ride["id"])

    assert response.status_code == 400
    assert "own ride" in response.json()["detail"]


def test_passenger_request_duplicate_and_rerequest_after_rejected(client, setup_college):
    driver_headers = register_and_login(client, "driver@aluno.ifsp.edu.br", "Driver")
    passenger_headers = register_and_login(client, "passenger@aluno.ifsp.edu.br", "Passenger")
    ride = create_ride(client, driver_headers)

    first = create_request(client, passenger_headers, ride["id"])
    duplicate = create_request(client, passenger_headers, ride["id"])
    reject = client.patch(
        f"/api/v1/ride-requests/{first.json()['id']}/reject",
        headers=driver_headers,
    )
    second = create_request(client, passenger_headers, ride["id"])

    assert first.status_code == 201
    assert duplicate.status_code == 400
    assert reject.status_code == 200
    assert reject.json()["status"] == "Rejected"
    assert second.status_code == 201


def test_only_driver_can_accept_request_and_phone_reveals_after_acceptance(client, setup_college):
    driver_headers = register_and_login(client, "driver@aluno.ifsp.edu.br", "Driver")
    passenger_headers = register_and_login(client, "passenger@aluno.ifsp.edu.br", "Passenger")
    other_headers = register_and_login(client, "other@aluno.ifsp.edu.br", "Other")
    ride = create_ride(client, driver_headers)
    request = create_request(client, passenger_headers, ride["id"]).json()

    unauthorized = client.patch(
        f"/api/v1/ride-requests/{request['id']}/accept",
        headers=other_headers,
    )
    before_accept = client.get("/api/v1/rides/mine", headers=driver_headers).json()
    accepted = client.patch(
        f"/api/v1/ride-requests/{request['id']}/accept",
        headers=driver_headers,
    )
    driver_view = client.get("/api/v1/rides/mine", headers=driver_headers).json()
    passenger_view = client.get("/api/v1/rides", headers=passenger_headers).json()
    passenger_notifications = client.get("/api/v1/notifications", headers=passenger_headers).json()

    assert unauthorized.status_code == 403
    assert before_accept[0]["requests"][0]["passenger"]["phone"] is None
    assert accepted.status_code == 200
    assert accepted.json()["status"] == "Accepted"
    assert driver_view[0]["requests"][0]["passenger"]["phone"] == "999999999"
    assert passenger_view[0]["rider_phone"] == "999999999"
    assert passenger_notifications[0]["title"] == "Solicitacao aceita"
    assert passenger_notifications[0]["read"] is False


def test_seat_limit_blocks_second_accept(client, setup_college):
    driver_headers = register_and_login(client, "driver@aluno.ifsp.edu.br", "Driver")
    passenger_headers = register_and_login(client, "passenger@aluno.ifsp.edu.br", "Passenger")
    passenger_two_headers = register_and_login(client, "passenger2@aluno.ifsp.edu.br", "Passenger Two")
    ride = create_ride(client, driver_headers, available_seats=1)
    first_request = create_request(client, passenger_headers, ride["id"]).json()
    second_request = create_request(client, passenger_two_headers, ride["id"]).json()

    first_accept = client.patch(
        f"/api/v1/ride-requests/{first_request['id']}/accept",
        headers=driver_headers,
    )
    second_accept = client.patch(
        f"/api/v1/ride-requests/{second_request['id']}/accept",
        headers=driver_headers,
    )

    assert first_accept.status_code == 200
    assert second_accept.status_code == 400
    assert "no available seats" in second_accept.json()["detail"]


def test_passenger_and_driver_cancellations(client, setup_college):
    driver_headers = register_and_login(client, "driver@aluno.ifsp.edu.br", "Driver")
    passenger_headers = register_and_login(client, "passenger@aluno.ifsp.edu.br", "Passenger")
    ride = create_ride(client, driver_headers)
    request = create_request(client, passenger_headers, ride["id"]).json()

    cancel_request = client.patch(
        f"/api/v1/ride-requests/{request['id']}/cancel",
        headers=passenger_headers,
    )
    driver_notifications = client.get("/api/v1/notifications", headers=driver_headers)
    cancel_ride = client.patch(f"/api/v1/rides/{ride['id']}/cancel", headers=driver_headers)
    available = client.get("/api/v1/rides", headers=passenger_headers)

    assert cancel_request.status_code == 200
    assert cancel_request.json()["status"] == "Cancelled"
    assert driver_notifications.json()[0]["title"] == "Solicitacao cancelada"
    assert cancel_ride.status_code == 200
    assert cancel_ride.json()["status"] == "Cancelled"
    assert available.json() == []


def test_reject_request_creates_notification_and_can_mark_read(client, setup_college):
    driver_headers = register_and_login(client, "driver@aluno.ifsp.edu.br", "Driver")
    passenger_headers = register_and_login(client, "passenger@aluno.ifsp.edu.br", "Passenger")
    ride = create_ride(client, driver_headers)
    request = create_request(client, passenger_headers, ride["id"]).json()

    rejected = client.patch(
        f"/api/v1/ride-requests/{request['id']}/reject",
        headers=driver_headers,
    )
    unread_notifications = client.get("/api/v1/notifications", headers=passenger_headers)
    read_notifications = client.patch("/api/v1/notifications/read", headers=passenger_headers)

    assert rejected.status_code == 200
    assert unread_notifications.json()[0]["title"] == "Solicitacao recusada"
    assert unread_notifications.json()[0]["read"] is False
    assert read_notifications.json()[0]["read"] is True


def test_cancel_ride_notifies_active_passengers(client, setup_college):
    driver_headers = register_and_login(client, "driver@aluno.ifsp.edu.br", "Driver")
    passenger_headers = register_and_login(client, "passenger@aluno.ifsp.edu.br", "Passenger")
    ride = create_ride(client, driver_headers)
    request = create_request(client, passenger_headers, ride["id"]).json()
    client.patch(
        f"/api/v1/ride-requests/{request['id']}/accept",
        headers=driver_headers,
    )

    cancelled = client.patch(f"/api/v1/rides/{ride['id']}/cancel", headers=driver_headers)
    notifications = client.get("/api/v1/notifications", headers=passenger_headers)

    assert cancelled.status_code == 200
    assert notifications.json()[0]["title"] == "Carona cancelada"
