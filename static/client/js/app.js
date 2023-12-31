let token = localStorage.getItem("access_token");

//const BASE_URL = "";

//console.log(`token=${token}`);

function showMessage(msg) {
  alert(msg);
}

function setLoading(target) {
  target.innerHTML = '<div class="alert alert-primary" role="alert">Loading...</div>';
}

get_refresh_token = async () => {
  get_refresh_token.counter = (get_refresh_token.counter || 0) + 1;
  if (get_refresh_token > 1) {
    console.log("get_refresh_token is busy, try later");
    return;
  }
  const URL = `${BASE_URL}/api/auth/refresh_token`;
  let refresh_token = localStorage.getItem("refresh_token");
  console.log(`refresh_token. token=${token}, refresh_token=${refresh_token}`);

  const response = await fetch(URL, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${refresh_token}`,
    },
  });

  if (response.ok) {
    result = await response.json();
    localStorage.setItem("access_token", result?.access_token);
    localStorage.setItem("refresh_token", result?.refresh_token);
    token = localStorage.getItem("access_token");
    // refresh_token = localStorage.getItem("refresh_token");
    get_refresh_token.counter = 0;
    return token;
  } else if (response.status == 401) {
    //window.location = "index.html";
    get_refresh_token.counter = 0;
  } else {
    get_refresh_token.counter = 0;
  }
  get_refresh_token.counter = 0;
};

// get_cats = async () => {
//   get_cats.counter = (get_cats.counter || 0) + 1;
//   setLoading(cats);
//   const URL = `${BASE_URL}/api/cats`;
//   const response = await fetch(URL, {
//     method: "GET",
//     headers: {
//       Authorization: `Bearer ${token}`,
//     },
//   });
//   if (response.ok) {
//     get_cats.counter = 0;
//     cats.innerHTML = "";
//     result = await response.json();
//     for (cat of result) {
//       el = document.createElement("li");
//       el.className = "list-group-item";
//       el.innerHTML = `ID: ${cat?.id} Name: <strong>${cat?.nickname}</strong> Status: ${cat?.vaccinated} Owner: ${cat?.owner.email}`;
//       cats.appendChild(el);
//     }
//   } else if (response.status == 401) {
//     if (get_cats.counter < 4) {
//       console.log(`Try: refresh_token counter: ${get_cats.counter}`);
//       token = await get_refresh_token();
//       setTimeout(get_cats, 3000);
//     } else {
//       console.log(`Try: to login page counter: ${get_cats.counter}`);
//       window.location = "index.html";
//     }
//   }
// };

get_profile = async () => {
  get_profile.counter = (get_profile.counter || 0) + 1;
  //setLoading(user_profile);
  const URL = `${BASE_URL}/api/users/profile/`;
  const response = await fetch(URL, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  if (response.ok) {
    get_profile.counter = 0;
    //user_profile.innerHTML = "";
    const user_profile_loading = document.getElementById("user_profile_loading");
    user_profile_loading?.classList.add("invisible");
    const user_profile = document.getElementById("user_profile");

    item = await response.json();
    if (item) {
      const username = document.getElementById("username");
      if (username) username.value = item?.username;
      // if (username) username.innerHTML = "Client1";
      const email = document.getElementById("email");
      if (email) email.innerHTML = item?.email;
      // if (email) email.innerHTML = "client1@example.com";
      const role = document.getElementById("role");
      if (role) role.innerHTML = item?.role;
      const avatar = document.getElementById("avatar");
      if (avatar) avatar.src = item?.avatar;
      const created_at = document.getElementById("created_at");
      if (created_at) {
        d = new Date(item?.created_at);
        created_at.innerHTML = d;
      }
      const images_count = document.getElementById("images_count");
      if (images_count) images_count.innerHTML = item?.images_count;
      const comments_count = document.getElementById("comments_count");
      if (comments_count) comments_count.innerHTML = item?.comments_count;

      // const el = document.createElement("li");
      // el.className = "list-group-item";
      // el.innerHTML = `ID: ${item?.id} ${item?.username}, Email: <strong>${item?.email}</strong>. Created: ${item?.created_at} `;
      // user_profile.appendChild(el);
      // const img = document.createElement("img");
      // img.src = item?.avatar;
      // user_profile.appendChild(img);
      user_profile?.classList.remove("invisible");
    }
  } else if (response.status == 401) {
    if (get_profile.counter < 4) {
      console.log(`Try: refresh_token counter: ${get_profile.counter}`);
      token = await get_refresh_token();
      setTimeout(get_profile, 3000);
    } else {
      window.location = "index.html";
    }
  }
};

// ownerCreate.addEventListener("submit", async (e) => {
//   e.preventDefault();
//   const URL = `${BASE_URL}/api/user_profile/`;
//   const raw = JSON.stringify({
//     email: ownerCreate?.email?.value,
//   });
//   const response = await fetch(URL, {
//     method: "POST",
//     headers: {
//       Authorization: `Bearer ${token}`,
//       "Content-Type": "application/json",
//     },
//     body: raw,
//   });
//   if (response.status == 201) {
//     ownerCreate.reset();
//     get_profile();
//   } else if (response.status == 401) {
//     token = await get_refresh_token();
//     console.log("Try again");
//   } else {
//     window.location = "index.html";
//   }
// });

const user_profile = document.getElementById("user_profile");

// get_cats();
get_profile();

// setTimeout(() => {
//   get_cats();
// }, 15000);
// setTimeout(()=>{get_cats},15000);

const form = document.getElementById("form_username");

form?.addEventListener("submit", async (e) => {
  e.preventDefault();
  const button = document.querySelector('input[type="submit"]');
  if (button) {
    button.setAttribute("disabled", true);
  }
  const t = e.target;
  const username = t.username.value;
  const data = {
    username: username,
  };
  const URL = `${BASE_URL}/api/users/me/`;
  await fetch(URL, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(data),
  })
    .then((response) => {
      if (button) {
        button.removeAttribute("disabled");
      }
      if (response.status >= 500) {
        throw "ERROR STATUS: " + response.status;
      }
      if (response.status < 400) {
        //window.location = "confirm.html";
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
    })
    .catch((err) => {
      console.log("ERROR", err);
      showMessage(err);
    });
});

const avatar_img = document.getElementById("avatar");
const avatar_upload = document.getElementById("avatar_upload");
const form_avatar = document.getElementById("form_avatar");



async function send_img(t) {
  // e.preventDefault();
  // const t = e.target;
  //t.preventDefault();
  //const  w =avatar_img.clientWidth ;
  avatar_img.src = "";
  //avatar_img.clientWidth=w;
  avatar_img.src = "/static/client/images/loading.gif"
  const formData = new FormData(t);
  const URL = `${BASE_URL}/api/users/avatar/`;
  await fetch(URL, {
    method: "PATCH",
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: formData,
  })
    .then((response) => {
      if (response.status >= 500) {
        throw "ERROR STATUS: " + response.status;
      }
      if (response.status < 400) {
        //window.location = "confirm.html";
      }
      return response.json();
    })
    .then((json) => {
      console.log(json);
      if (json?.avatar) {
          avatar_img.src = json?.avatar;
      }
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
    })
    .catch((err) => {
      console.log("ERROR", err);
      showMessage(err);
    });
};

form_avatar.addEventListener("submit", send_img);

avatar_img?.addEventListener("click", async (e) => {
  e.preventDefault();
  avatar_upload?.click();
});

avatar_upload?.addEventListener("change", (e) => {
  e.preventDefault();
  //form_avatar.submit();
  send_img(form_avatar);
});
