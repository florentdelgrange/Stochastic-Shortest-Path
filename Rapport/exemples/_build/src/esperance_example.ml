open Gauss_pivot

let a =
  [|
    [| 1./.2.; -1./.5.; -1./.5.; -1./.10. |];
    [| -1./.5.; 3./.5.; -1./.5.; -1./.5. |];
    [| -1./.5.; -1./.5.; 3./.5.; -1./.5. |];
    [| 0.; 0.; 0.; 1. |]
  |]

let b = [| 5.; 3.; 2.; 0. |]

let x = resolve a b

let () =
  Array.iter (fun s -> Printf.printf "%.15F " s) x;
  Printf.printf "\n"
