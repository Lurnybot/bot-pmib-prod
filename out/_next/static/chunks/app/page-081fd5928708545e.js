(self.webpackChunk_N_E = self.webpackChunk_N_E || []).push([
  [931],
  {
    6578: function (e, t, s) {
      Promise.resolve().then(s.bind(s, 50));
    },
    50: function (e, t, s) {
      "use strict";
      s.d(t, {
        Chatbot: function () {
          return a;
        },
      });
      var n = s(7437),
        r = s(2265),
        o = s(8904),
        i = s(920);
      s(741);
      let a = (e) => {
        let {
            botTitle: t,
            botImage: s,
            botMessageBgColor: a,
            userMessageBgColor: l,
            bgcolor: d,
          } = e,
          [c, h] = (0, r.useState)([]),
          [u, x] = (0, r.useState)(""),
          [g, p] = (0, r.useState)(!1),
          [m, j] = (0, r.useState)(null),
          f = (0, r.useRef)(null);
        (0, r.useEffect)(() => {
          let e = localStorage.getItem("sessionId");
          e || ((e = (0, i.Z)()), localStorage.setItem("sessionId", e)),
            j(e),
            h([
              {
                sender: "Bot",
                text: "Hello! I am **Mitra** - PMI Bangalore Chapter's virtual assistant! \uD83D\uDC4B \n\nHow can I assist you today?",
            },
            ]);
        }, []),
          (0, r.useEffect)(() => {
            f.current && f.current.scrollIntoView({ behavior: "smooth" });
          }, [c]);
        let y = async () => {
          let e = u.trim();
          if ("" !== e && m) {
            x(""), h((t) => [...t, { sender: "You", text: e }]), p(!0);
            try {
              var t;
              let s = await fetch("/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ query: e, sessionId: m }),
              });
              if (!s.ok) throw Error("Failed to send the query.");
              let n =
                  null === (t = s.body) || void 0 === t
                    ? void 0
                    : t.getReader(),
                r = new TextDecoder(),
                o = "";
              for (; n; ) {
                let { value: e, done: t } = await n.read();
                if (t) break;
                let s = r.decode(e, { stream: !0 });
                (o += s),
                  h((e) => {
                    let t = e[e.length - 1];
                    return t && "Bot" === t.sender
                      ? [
                          ...e.slice(0, e.length - 1),
                          { sender: "Bot", text: o },
                        ]
                      : [...e, { sender: "Bot", text: o }];
                  });
              }
            } catch (e) {
              console.error("Error streaming response:", e),
                h((e) => [
                  ...e,
                  {
                    sender: "Bot",
                    text: "We have temporarily disabled the service, Please contact the Admin. \uD83D\uDE0A",
                  },
                ]);
            } finally {
              p(!1);
            }
          }
        };
        return (0, n.jsxs)("div", {
          id: "chatbox",
          style: { backgroundColor: d },
          children: [
            (0, n.jsxs)("div", {
              id: "chat-header",
              children: [
                (0, n.jsxs)("div", {
                  id: "chat-info",
                  children: [
                    (0, n.jsx)("img", { src: s, alt: "Chatbot" }),
                    (0, n.jsxs)("div", {
                      id: "chat-text",
                      children: [
                        (0, n.jsx)("span", { id: "chat-title", children: t }),
                        " ",
                        (0, n.jsxs)("div", {
                          id: "online-status",
                          children: [
                            (0, n.jsx)("span", { id: "status-dot" }),
                            (0, n.jsx)("span", {
                              id: "chat-status",
                              children: "Online",
                            }),
                          ],
                        }),
                      ],
                    }),
                  ],
                }),
                (0, n.jsx)("button", {
                  onClick: () => {
                    window.parent.postMessage("closeChat", "*");
                  },
                  style: {
                    background: "none",
                    border: "none",
                    fontSize: "20px",
                    cursor: "pointer",
                    color: "#333",
                    position: "absolute",
                    top: 10,
                    right: 10,
                    zIndex: 10,
                  },
                  children: "\xd7",
                }),
              ],
            }),
            (0, n.jsxs)("div", {
              id: "messages",
              children: [
                c.map((e, t) =>
                  (0, n.jsx)(
                    "div",
                    {
                      className: "message ".concat(
                        "You" === e.sender ? "user" : "bot"
                      ),
                      children:
                        "You" === e.sender
                          ? (0, n.jsx)("div", {
                              className: "message-content",
                              style: {
                                backgroundColor: "You" === e.sender ? l : a,
                              },
                              children: e.text,
                            })
                          : (0, n.jsxs)(n.Fragment, {
                              children: [
                                (0, n.jsx)("img", {
                                  src: s,
                                  alt: "Bot",
                                  className: "bot-image",
                                }),
                                (0, n.jsx)("div", {
                                  className: "message-content",
                                  style: {
                                    backgroundColor: "You" === e.sender ? l : a,
                                  },
                                  children: (0, n.jsx)(o.U, {
                                    components: {
                                      a: (e) => {
                                        let { node: t, ...s } = e;
                                        return (0, n.jsx)("a", {
                                          ...s,
                                          target: "_blank",
                                          rel: "noopener noreferrer",
                                          children: s.children,
                                        });
                                      },
                                    },
                                    children: e.text,
                                  }),
                                }),
                              ],
                            }),
                    },
                    t
                  )
                ),
                g &&
                  (0, n.jsxs)("div", {
                    className: "message bot",
                    children: [
                      (0, n.jsx)("img", {
                        src: s,
                        alt: "Bot",
                        className: "bot-image",
                      }),
                      (0, n.jsx)("div", {
                        className: "message-content",
                        children: "Typing...",
                      }),
                    ],
                  }),
                (0, n.jsx)("div", { ref: f }),
              ],
            }),
            (0, n.jsxs)("div", {
              id: "input-container",
              children: [
                (0, n.jsx)("input", {
                  id: "input",
                  type: "text",
                  value: u,
                  onChange: (e) => x(e.target.value),
                  placeholder: "Type a message...",
                  onKeyDown: (e) => {
                    "Enter" === e.key && (e.preventDefault(), y());
                  },
                }),
                (0, n.jsx)("button", {
                  id: "send-button",
                  onClick: y,
                  children: (0, n.jsx)("img", {
                    src: "/send_arrow.png",
                    alt: "Send",
                    style: {
                      width: "24px",
                      height: "24px",
                      objectFit: "contain",
                    },
                  }),
                }),
              ],
            }),
            (0, n.jsx)("div", {
              id: "footer",
              children: (0, n.jsxs)("span", {
                style: { display: "flex", alignItems: "center" },
                children: [
                  "Powered by",
                  " ",
                  (0, n.jsxs)("a", {
                    href: "https://lurnybot.com",
                    target: "_blank",
                    rel: "noopener noreferrer",
                    style: {
                      display: "inline-flex",
                      alignItems: "center",
                      fontWeight: "bold",
                      marginLeft: "5px",
                    },
                    children: [
                      (0, n.jsx)("img", {
                        src: "/LurnyBot.jpeg",
                        alt: "LurnyBot",
                        style: {
                          width: "16px",
                          height: "16px",
                          borderRadius: "50%",
                          marginRight: "5px",
                        },
                      }),
                      "LurnyBot",
                    ],
                  }),
                ],
              }),
            }),
            " ",
          ],
        });
      };
    },
    741: function () {},
  },
  function (e) {
    e.O(0, [720, 537, 971, 23, 744], function () {
      return e((e.s = 6578));
    }),
      (_N_E = e.O());
  },
]);
