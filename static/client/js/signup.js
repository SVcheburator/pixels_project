//const BASE_URL = "";

function setCookie(cname, cvalue, expire) {
  const d = new Date(expire);
  const expires = "expires=" + d.toUTCString();
  const cookie = cname + "=" + cvalue + ";" + expires + ";path=/;";
  document.cookie = cookie;
}

const form = document.forms[0];

form?.addEventListener("submit", async (e) => {
  e.preventDefault();
  const t = e.target;
  const username = t.username.value;
  const email = t.email.value;
  const password = t.password.value;
  const URL = `${BASE_URL}/api/auth/signup`;
  await fetch(URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: new URLSearchParams({
      username: username,
      email: email,
      password: password,
    }),
  })
    .then((response) => {
      if (response.status != 201) {
        throw "ERROR STATUS: " + response.status;
      }
      return response.json();
    })
    .then((json) => {
      console.log(json);
      setTimeout(() => {
        window.location = "index.html";
      }, 500);
      // if (json?.token_type == "bearer") {
      //   // setCookie("access_token", json?.access_token, json?.expire_access_token);
      //   // setCookie("refresh_token", json?.refresh_token, json?.expire_refresh_token);
      //   localStorage.setItem("access_token", json?.access_token);
      //   localStorage.setItem("refresh_token", json?.refresh_token);
      // }
    })
    .catch((err) => {
      console.log("ERROR", err);
      setTimeout(() => {
        window.location = "?error=Signup error code :"+err;
      }, 500);
    });
});

const queryString = window.location.search;
const urlParams = new URLSearchParams(queryString);
const error_msg = urlParams.get('error')
console.log("error_msg", error_msg)
if (error_msg){
  alert(error_msg)
}
