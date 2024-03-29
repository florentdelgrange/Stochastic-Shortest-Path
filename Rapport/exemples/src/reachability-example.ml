open Gauss_pivot

let a =
  [|
    [| 1.; -1./.5.; -1./.5.; -2./.5.; 0.; 0.; 0. |];
    [| 0.; 1.; -1./.3.; 0.; 0.; 0.; 0. |];
    [| 0.; -1./.4.; 1./.4.; 0.; 0.; 0.; 0. |];
    [| 0.; 0.; 0.; 1.; 0.; 0.; 0. |];
    [| 0.; 0.; 0.; 0.; 1.; 0.; 0. |];
    [| 0.; 0.; 0.; 0.; 0.; 1.; 0. |];
    [| 0.; 0.; 0.; 0.; 0.; 0.; 1. |]
  |]

let b = [| 1./.5.; 2./.3.; 0.; 0.; 0.; 1.; 1. |]

let x = resolve a b

let () =
  Array.iter (fun s -> Printf.printf "%.15F " s) x;
  Printf.printf "\n"
