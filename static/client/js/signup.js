//const BASE_URL = "";

function setCookie(cname, cvalue, expire) {
  const d = new Date(expire);
  const expires = "expires=" + d.toUTCString();
  const cookie = cname + "=" + cvalue + ";" + expires + ";path=/;";
  document.cookie = cookie;
}

function showMessage(msg) {
  alert(msg);
}

const form = document.forms[0];

form?.addEventListener("submit", async (e) => {
  e.preventDefault();
  const t = e.target;
  const username = t.username.value;
  const email = t.email.value;
  const password = t.password.value;
  const data = {
    username: username,
    email: email,
    password: password,
  };
  const URL = `${BASE_URL}/api/auth/signup`;
  await fetch(URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  })
    .then((response) => {
      if (response.status >= 500) {
        throw "ERROR STATUS: " + response.status;
      }
      if (response.status == 201) {
        window.location = "confirm.html";
      }

      return response.json();
    })
    .then((json) => {
      console.log(json);
      detail = json?.detail;
      err = "";
      if (Array.isArray(detail)) {
        for (const d of detail) {
          const loc = d.loc[1];
          const mgs = d.msg;
          err = err + " " + loc + ": " + mgs;
          console.log(d);
        }
      } else {
        err = detail;
      }
      if (err) {
        showMessage(err);
      }
      // setTimeout(() => {
      //   window.location = "?error=Signup error code " + err;
      // }, 500);
    })
    .catch((err) => {
      console.log("ERROR", err);
      showMessage(err);
      // setTimeout(() => {
      //   window.location = "?error=Signup error code " + err;
      // }, 500);
    });
});

// const queryString = window.location.search;
// const urlParams = new URLSearchParams(queryString);
// const error_msg = urlParams.get("error");
// console.log("error_msg", error_msg);
// if (error_msg) {
//   alert(error_msg);
// }
