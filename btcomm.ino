#include <DC_driver.h>
#include "comm.h"

DC_driver motor_1(7, 8, 6);
DC_driver motor_2(4, 2, 5);
DC_driver motor_3(A1, A0, 10);
DC_driver motor_4(12, 11, 9);

// NOTE(Richo): While Arduino UNO R3 has just one serial port, the UNO R4 has two:
// Serial for the USB-C and Serial1 for the RX/TX pins. So the next line allows to
// choose which serial to use for the comm protocol.
HardwareSerial* serial = &Serial1;
Comm comm(serial);
const int MOT4 = 0;

void setup() 
{
  motor_1.begin();
  motor_2.begin();
  motor_3.begin();
  motor_4.begin();

  serial->begin(9600);
}

void loop() 
{
  Message msg;
  bool has_msg = comm.check_incoming(&msg);
  if (has_msg) 
  {
    if (msg.type == SET_MOTORS)
    {
      handle_set_motors(&msg.set_motors);
    }
    else if (msg.type == TURN)
    {
      handle_turn(&msg.turn);
    }
    else if (msg.type == MOVE_LR)
    {
      handle_move_lr(&msg.move_lr);
    }
    else
    {
      serial->println("ERROR: NO MESSAGE!");
    }
  }
}

void handle_set_motors(SetMotorsPayload* payload) 
{
  motor_1.analogMove(payload->direction[0], payload->speed[0]);
  motor_2.analogMove(payload->direction[1], payload->speed[1]);
  motor_3.analogMove(payload->direction[2], payload->speed[2]);
  motor_4.analogMove(payload->direction[3], payload->speed[3]+MOT4);

  // TODO(Richo): This is just for debugging...
  serial->print("SET_MOTORS: [");
  for (int i = 0; i < 4; i++) 
  {
    if (i > 0) serial->print(", ");
    serial->print("(");
    if (payload->direction[i]) 
    {
      serial->print("F");
    } 
    else 
    {
      serial->print("B");
    }
    serial->print(" ");
    serial->print((int)payload->speed[i]);
    serial->print(")");
  }
  serial->println("]");
}

void handle_turn(TurnPayload* payload)
{
  motor_1.analogMove(payload->is_clockwise, payload->speed);
  motor_2.analogMove(payload->is_clockwise, payload->speed);
  motor_3.analogMove(payload->is_clockwise, payload->speed);
  motor_4.analogMove(payload->is_clockwise, payload->speed+MOT4);

  // TODO(Richo): This is just for debugging...
  serial->print("TURN: ");
  serial->print(payload->is_clockwise);
  serial->print(", ");
  serial->println(payload->speed);
}


void handle_move_lr(MoveLRPayload* payload)
{
  motor_1.analogMove(!payload->is_left, payload->speed);
  motor_2.analogMove(payload->is_left, payload->speed);
  motor_3.analogMove(payload->is_left, payload->speed);
  motor_4.analogMove(!payload->is_left, payload->speed+MOT4);

  // TODO(Richo): This is just for debugging...
  serial->print("MOVE_LR: ");
  serial->print(payload->is_left);
  serial->print(", ");
  serial->println(payload->speed);
}

