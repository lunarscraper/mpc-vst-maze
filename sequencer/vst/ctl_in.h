/* ctl_in.h - "Control In": MIDI CCs from hardware controllers, for a plugin that already owns an
 * ALSA sequencer client (opened SND_SEQ_OPEN_DUPLEX, non-blocking).
 *
 * MPC OS gives a plugin no way to pick a MIDI input, so the plugin makes its own: a second port
 * "Control In" that subscribes itself to every hardware MIDI input (USB controllers, the DIN input),
 * also ones plugged in later (system announce port). ctl_poll() is called once per audio block and
 * hands every controller event to the plugin, which filters by its own "Control Ch" parameter.
 *
 * Same file in mpc-vst-euclidier (inline there), mpc-vst-acid and mpc-vst-maze. Needs LOG() and a
 * CTL_TAG string (log prefix) defined before the include. */
#ifndef MPC_CTL_IN_H
#define MPC_CTL_IN_H
#include <alsa/asoundlib.h>

struct CtlIn {
    int port = -1;
    long seen = 0, used = 0;   /* per log period: controller events that arrived / that were applied */
};
typedef void (*ctl_cc_fn)(void *user, int ch, int cc, int val);   /* ch 0..15 */

/* Subscribe Control In to one hardware MIDI input. Other plugins' virtual ports are left alone. */
static inline void ctl_subscribe(snd_seq_t *seq, CtlIn *c, int client, int port) {
    if (!seq || c->port < 0 || client == snd_seq_client_id(seq) || client == SND_SEQ_CLIENT_SYSTEM) return;
    snd_seq_port_info_t *pi;
    snd_seq_port_info_alloca(&pi);
    if (snd_seq_get_any_port_info(seq, client, port, pi) < 0) return;
    unsigned cap = snd_seq_port_info_get_capability(pi), type = snd_seq_port_info_get_type(pi);
    const unsigned need = SND_SEQ_PORT_CAP_READ | SND_SEQ_PORT_CAP_SUBS_READ;
    if ((cap & need) != need || (cap & SND_SEQ_PORT_CAP_NO_EXPORT) || !(type & SND_SEQ_PORT_TYPE_HARDWARE)) return;
    int rc = snd_seq_connect_from(seq, c->port, client, port);
    LOG(CTL_TAG " control in <- %d:%d '%s'%s\n", client, port, snd_seq_port_info_get_name(pi),
        rc < 0 ? " (already connected or refused)" : "");
}
static inline void ctl_open(snd_seq_t *seq, CtlIn *c) {
    if (!seq) return;
    c->port = snd_seq_create_simple_port(seq, "Control In",
        SND_SEQ_PORT_CAP_WRITE | SND_SEQ_PORT_CAP_SUBS_WRITE,
        SND_SEQ_PORT_TYPE_MIDI_GENERIC | SND_SEQ_PORT_TYPE_APPLICATION);
    if (c->port < 0) { LOG(CTL_TAG " no Control In port\n"); return; }
    snd_seq_connect_from(seq, c->port, SND_SEQ_CLIENT_SYSTEM, SND_SEQ_PORT_SYSTEM_ANNOUNCE);   /* hot-plug */
    snd_seq_client_info_t *ci;
    snd_seq_port_info_t *pi;
    snd_seq_client_info_alloca(&ci);
    snd_seq_port_info_alloca(&pi);
    snd_seq_client_info_set_client(ci, -1);
    while (snd_seq_query_next_client(seq, ci) >= 0) {
        int cl = snd_seq_client_info_get_client(ci);
        snd_seq_port_info_set_client(pi, cl);
        snd_seq_port_info_set_port(pi, -1);
        while (snd_seq_query_next_port(seq, pi) >= 0) ctl_subscribe(seq, c, cl, snd_seq_port_info_get_port(pi));
    }
}
/* Audio thread: drain Control In without blocking. */
static inline void ctl_poll(snd_seq_t *seq, CtlIn *c, ctl_cc_fn fn, void *user) {
    if (!seq || c->port < 0) return;
    snd_seq_event_t *ev = nullptr;
    for (int guard = 0; guard < 256 && snd_seq_event_input_pending(seq, 1) > 0; guard++) {
        if (snd_seq_event_input(seq, &ev) < 0 || !ev) break;
        if (ev->type == SND_SEQ_EVENT_CONTROLLER) {
            c->seen++;
            fn(user, ev->data.control.channel, (int)ev->data.control.param, ev->data.control.value);
        } else if (ev->type == SND_SEQ_EVENT_PORT_START) {
            ctl_subscribe(seq, c, ev->data.addr.client, ev->data.addr.port);
        }
    }
}
#endif
