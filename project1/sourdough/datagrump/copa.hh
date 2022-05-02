#ifndef COPA_HH
#define COPA_HH

#include <cstdint>
#include <queue>
#include <set>

class Copa
{
private:
  bool debug_;
  double window_size = 1.0;

  // parameters
  double delta = 0.5;
  // velocity
  double v = 2.0; 
  uint64_t v_ack_sent = 0;
  int v_ack_count_rtt = 0;
  bool v_up = true;
  double v_window = 1.0;

  // RTT queue
  std::queue<int> Q;
  std::multiset<int> standing_rtt;
  double minRTT = 42.0;

  void inc();
  void dec();

public:
  Copa( const bool debug );
  unsigned int get_window_size();
  void ack_received( const uint64_t send_timestamp_acked,
		     const uint64_t timestamp_ack_received );
};

#endif

